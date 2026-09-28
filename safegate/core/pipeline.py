"""
SafeGate Core Pipeline
Máy trạng thái (State Machine) điều phối toàn bộ quy trình kiểm tra cổng:
1. SCANNING_QR: Quét mã QR trên thẻ nhân viên để định danh.
2. CHECKING_PPE: Nhận diện người, mũ, áo bằng AI + Kiểm tra luật hình học + Voting 8/10 frame.
3. SHOWING_RESULT: Hiển thị kết quả PASS (Xanh) / FAIL (Đỏ) và lưu log SQLite (KHÔNG LƯU ẢNH).
4. COOLDOWN: Đợi 3 giây trước khi sẵn sàng cho lượt tiếp theo.
"""
import time
from enum import Enum
from typing import Optional, Dict, Tuple, List, Any
import numpy as np
from safegate.config import RESULT_DISPLAY_SEC
from safegate.database.db_manager import DatabaseManager
from safegate.core.detector import PPEDetector
from safegate.core.geometric_rules import GeometricRuleValidator, EvaluationResult
from safegate.core.frame_voting import MultiFrameVoter
from safegate.core.qr_scanner import QRScanner
from safegate.utils.visualizer import GateVisualizer

class GateState(Enum):
    SCANNING_QR = "SCANNING_QR"
    CHECKING_PPE = "CHECKING_PPE"
    SHOWING_RESULT = "SHOWING_RESULT"

class SafeGatePipeline:
    def __init__(self,
                 db_manager: Optional[DatabaseManager] = None,
                 detector: Optional[PPEDetector] = None):
        self.db = db_manager or DatabaseManager()
        self.detector = detector or PPEDetector()
        self.geometric_validator = GeometricRuleValidator()
        self.voter = MultiFrameVoter()
        self.qr_scanner = QRScanner(self.db)
        self.visualizer = GateVisualizer()

        # Trạng thái hiện tại
        self.state: GateState = GateState.SCANNING_QR
        self.current_employee: Optional[Dict[str, Any]] = None
        self.final_status: str = "CHECKING"  # PASS hoặc FAIL
        self.final_missing_items: List[str] = []
        self.result_start_time: float = 0.0

        # Thống kê hiệu năng
        self.fps: float = 0.0
        self.last_frame_time: float = time.time()

    def reset_to_scan_state(self):
        """Khởi động lại trạng thái chờ quét mã nhân viên"""
        self.state = GateState.SCANNING_QR
        self.current_employee = None
        self.final_status = "CHECKING"
        self.final_missing_items = []
        self.result_start_time = 0.0
        self.voter.reset()

    def trigger_manual_check(self, mock_code: str = "NV-1001"):
        """Chuyển thẳng sang bước kiểm tra PPE (bỏ qua bước QR) phục vụ test nhanh"""
        emp = self.db.get_employee_by_code(mock_code)
        if not emp:
            emp = {
                "employee_code": mock_code,
                "full_name": "Công nhân thử nghiệm",
                "department": "Bộ phận kỹ thuật",
                "role": "Kiểm thử"
            }
        self.current_employee = emp
        self.state = GateState.CHECKING_PPE
        self.voter.start_session()

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Xử lý 1 khung hình từ video stream:
        Thực hiện theo máy trạng thái và vẽ visual trực quan lên frame
        """
        if frame is None:
            return frame

        # Tính FPS
        now = time.time()
        dt = now - self.last_frame_time
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)
        self.last_frame_time = now

        h, w = frame.shape[:2]
        annotated_frame = frame.copy()

        # =======================================================
        # GIAI ĐOẠN 1: QUÉT THẺ NHÂN VIÊN (SCANNING_QR)
        # =======================================================
        if self.state == GateState.SCANNING_QR:
            emp, qr_points = self.qr_scanner.scan_frame(frame)
            self.visualizer.draw_qr_scan_zone(annotated_frame, qr_points)
            self.visualizer.draw_hud_header(
                annotated_frame,
                state_name="CHỜ QUÉT THẺ",
                employee=None,
                fps=self.fps,
                voting_score_str="0/10",
                progress_ratio=0.0
            )

            if emp:
                # Quét thẻ thành công! Chuyển sang kiểm tra đồ bảo hộ
                self.current_employee = emp
                self.state = GateState.CHECKING_PPE
                self.voter.start_session()

        # =======================================================
        # GIAI ĐOẠN 2: KIỂM TRA PPE (CHECKING_PPE)
        # =======================================================
        elif self.state == GateState.CHECKING_PPE:
            # 1. Nhận diện person, helmet, vest
            detections = self.detector.detect(frame)

            # 2. Kiểm tra bằng luật hình học
            eval_res = self.geometric_validator.evaluate_frame(detections, w, h)

            # 3. Vẽ bounding box và nhãn
            self.visualizer.draw_detections(annotated_frame, detections, eval_res)

            # 4. Đưa vào bộ lọc Voting nhiều frame (8/10)
            status, progress_ratio, missing = self.voter.add_frame(eval_res)

            # Vẽ HUD
            self.visualizer.draw_hud_header(
                annotated_frame,
                state_name="ĐANG KIỂM TRA PPE",
                employee=self.current_employee,
                fps=self.fps,
                voting_score_str=self.voter.current_score_str,
                progress_ratio=progress_ratio
            )

            # Nếu chốt kết quả PASS hoặc FAIL
            if status in ("PASS", "FAIL"):
                self.final_status = status
                self.final_missing_items = missing
                self.state = GateState.SHOWING_RESULT
                self.result_start_time = time.time()

                # GHI LOG VÀO SQLITE (TUYỆT ĐỐI KHÔNG LƯU ẢNH)
                if self.current_employee:
                    self.db.log_access(
                        employee_code=self.current_employee.get("employee_code", "UNKNOWN"),
                        employee_name=self.current_employee.get("full_name", "Không rõ"),
                        department=self.current_employee.get("department", "Không rõ"),
                        status=self.final_status,
                        missing_items=self.final_missing_items,
                        vote_score=self.voter.current_score_str,
                        duration=self.voter.elapsed_time
                    )

        # =======================================================
        # GIAI ĐOẠN 3: HIỂN THỊ KẾT QUẢ (SHOWING_RESULT)
        # =======================================================
        elif self.state == GateState.SHOWING_RESULT:
            # Tiếp tục vẽ detection nếu có
            detections = self.detector.detect(frame)
            eval_res = self.geometric_validator.evaluate_frame(detections, w, h)
            self.visualizer.draw_detections(annotated_frame, detections, eval_res)

            # Vẽ HUD Header
            self.visualizer.draw_hud_header(
                annotated_frame,
                state_name=f"KẾT QUẢ: {self.final_status}",
                employee=self.current_employee,
                fps=self.fps,
                voting_score_str=self.voter.current_score_str,
                progress_ratio=1.0 if self.final_status == "PASS" else 0.0
            )

            # Hiển thị Banner PASS (Xanh) hoặc FAIL (Đỏ) lớn
            self.visualizer.draw_result_banner(
                annotated_frame,
                status=self.final_status,
                missing_items=self.final_missing_items
            )

            # Sau 3 giây (RESULT_DISPLAY_SEC), tự động chuyển về chờ người tiếp theo
            if (time.time() - self.result_start_time) >= RESULT_DISPLAY_SEC:
                self.reset_to_scan_state()

        return annotated_frame
