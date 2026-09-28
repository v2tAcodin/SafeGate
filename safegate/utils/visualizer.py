"""
Visualizer Module for SafeGate
Vẽ giao diện trực quan trực tiếp lên khung hình Video:
- HUD Công nghiệp hiện đại (Industrial AI Aesthetic).
- Bounding Box thông minh kèm nhãn, độ tin cậy.
- Khung quét mã QR với hiệu ứng góc ngắm mục tiêu.
- Thanh tiến độ Voting đa khung hình (8/10).
- Banner kết quả kích thước lớn: PASS (Xanh lá) / FAIL (Đỏ) và danh sách đồ bảo hộ còn thiếu.
"""
from __future__ import annotations
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from safegate.core.geometric_rules import DetectionBox, EvaluationResult

# Bảng màu chuẩn BGR
COLOR_BG_DARK = (24, 24, 27)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_ACCENT_CYAN = (235, 180, 50)
COLOR_PASS_GREEN = (50, 205, 50)
COLOR_FAIL_RED = (50, 50, 230)
COLOR_WARNING_YELLOW = (0, 215, 255)
COLOR_BOX_PERSON = (220, 160, 40)
COLOR_BOX_HELMET = (0, 215, 255)
COLOR_BOX_VEST = (0, 255, 128)

class GateVisualizer:
    def __init__(self):
        # Font chữ OpenCV
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_glass_rect(self, img: np.ndarray, x: int, y: int, w: int, h: int,
                        color: Tuple[int, int, int], alpha: float = 0.6):
        """Vẽ hình chữ nhật mờ nền kiểu kính mờ (Glassmorphism)"""
        overlay = img.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    def draw_corner_brackets(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int,
                             color: Tuple[int, int, int], length: int = 25, thickness: int = 3):
        """Vẽ 4 góc vuông hiện đại kiểu ngắm mục tiêu"""
        # Góc trên - trái
        cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
        cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
        # Góc trên - phải
        cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
        cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
        # Góc dưới - trái
        cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
        cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
        # Góc dưới - phải
        cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
        cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)

    def draw_detections(self, frame: np.ndarray, detections: List[DetectionBox], eval_res: EvaluationResult):
        """Vẽ bounding box của các đối tượng với màu phân biệt"""
        for d in detections:
            x1, y1, x2, y2 = int(d.x1), int(d.y1), int(d.x2), int(d.y2)

            if d.class_name == "person":
                color = COLOR_BOX_PERSON
                label = f"Nguoi [{d.confidence:.2f}]"
            elif d.class_name == "helmet":
                # Đỏ nếu đang cầm tay, Vàng nếu đội trên đầu
                if eval_res.is_holding_helmet and d == eval_res.matched_helmet:
                    color = COLOR_FAIL_RED
                    label = "MU CAM TAY (Loi)"
                else:
                    color = COLOR_BOX_HELMET
                    label = f"Mu bao ho [{d.confidence:.2f}]"
            elif d.class_name == "vest":
                color = COLOR_BOX_VEST
                label = f"Ao phan quang [{d.confidence:.2f}]"
            else:
                color = (200, 200, 200)
                label = d.class_name

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Nhãn
            (tw, th), _ = cv2.getTextSize(label, self.font, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 6, y1), color, -1)
            cv2.putText(frame, label, (x1 + 3, y1 - 4), self.font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    def draw_qr_scan_zone(self, frame: np.ndarray, qr_points: Optional[np.ndarray] = None):
        """Vẽ khung hướng dẫn quét thẻ QR ở chính giữa màn hình"""
        h, w = frame.shape[:2]
        box_size = int(min(w, h) * 0.45)
        cx, cy = w // 2, h // 2
        x1, y1 = cx - box_size // 2, cy - box_size // 2
        x2, y2 = cx + box_size // 2, cy + box_size // 2

        # Làm tối nhẹ vùng ngoài khung quét để làm nổi bật tâm
        self.draw_corner_brackets(frame, x1, y1, x2, y2, COLOR_ACCENT_CYAN, length=35, thickness=4)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 100), 1)

        # Nếu phát hiện QR, vẽ viền xanh quanh QR
        if qr_points is not None and len(qr_points) > 0:
            pts = qr_points.astype(int).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=COLOR_PASS_GREEN, thickness=4)

        # Dòng hướng dẫn
        guide_text = "VUI LONG DUA THE NHAN VIEN (MA QR) VAO KHUNG"
        (tw, th), _ = cv2.getTextSize(guide_text, self.font, 0.65, 2)
        cv2.putText(frame, guide_text, (cx - tw // 2, y1 - 20), self.font, 0.65, COLOR_ACCENT_CYAN, 2, cv2.LINE_AA)

    def draw_hud_header(self, frame: np.ndarray, state_name: str, employee: Optional[Dict],
                        fps: float, voting_score_str: str, progress_ratio: float):
        """Vẽ thanh thông tin trạng thái đỉnh màn hình (HUD Header)"""
        w = frame.shape[1]
        header_h = 75

        # Nền Header
        self.draw_glass_rect(frame, 0, 0, w, header_h, (20, 24, 30), alpha=0.85)
        cv2.line(frame, (0, header_h), (w, header_h), (60, 65, 80), 2)

        # Tiêu đề hệ thống
        cv2.putText(frame, "SAFEGATE", (20, 32), self.font, 0.85, COLOR_TEXT_WHITE, 2, cv2.LINE_AA)
        cv2.putText(frame, "AI PPE GATE-CHECK", (20, 58), self.font, 0.45, COLOR_ACCENT_CYAN, 1, cv2.LINE_AA)

        # Thông tin nhân viên (nếu đã quét)
        if employee:
            emp_info = f"Nhan vien: {employee.get('full_name', 'Unknown')} ({employee.get('employee_code', '')})"
            dept_info = f"Bo phan: {employee.get('department', 'N/A')}"
            cv2.putText(frame, emp_info, (240, 32), self.font, 0.65, (240, 240, 240), 2, cv2.LINE_AA)
            cv2.putText(frame, dept_info, (240, 58), self.font, 0.5, (180, 180, 180), 1, cv2.LINE_AA)
        else:
            cv2.putText(frame, "Trang thai: Cho quet the dinh danh...", (240, 45), self.font, 0.65, (160, 160, 160), 1, cv2.LINE_AA)

        # Voting Progress Bar (ở góc phải)
        bar_w = 180
        bar_h = 16
        bar_x = w - bar_w - 140
        bar_y = 22
        
        cv2.putText(frame, f"Voting: {voting_score_str}", (bar_x, bar_y - 6), self.font, 0.45, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
        fill_w = int(bar_w * progress_ratio)
        if fill_w > 0:
            fill_color = COLOR_PASS_GREEN if progress_ratio >= 0.8 else COLOR_WARNING_YELLOW
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), fill_color, -1)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (120, 120, 120), 1)

        # FPS
        cv2.putText(frame, f"{fps:.1f} FPS", (w - 100, 45), self.font, 0.65, COLOR_PASS_GREEN, 2, cv2.LINE_AA)

    def draw_result_banner(self, frame: np.ndarray, status: str, missing_items: List[str]):
        """
        Hiển thị Banner kết quả khổng lồ trực quan:
        PASS (Xanh) hoặc FAIL (Đỏ) và liệt kê món còn thiếu
        """
        h, w = frame.shape[:2]
        banner_h = 170
        banner_y = h - banner_h - 20
        banner_x = 40
        banner_w = w - 80

        if status == "PASS":
            bg_color = (25, 130, 40)
            title = "PASS - DU DIEU KIEN VAO KHU VUC LAM VIEC"
            sub = "Da kiem tra: Day du Mu bao ho va Ao phan quang quy chuan"
            border_color = COLOR_PASS_GREEN
        else:
            bg_color = (30, 30, 170)
            title = "FAIL - KHONG DAT YEU CAU AN TOAN"
            missing_str = ", ".join(missing_items) if missing_items else "Thieu trang bi bao ho"
            sub = f"CAN BO SUNG: {missing_str.upper()}"
            border_color = COLOR_FAIL_RED

        # Nền banner
        self.draw_glass_rect(frame, banner_x, banner_y, banner_w, banner_h, bg_color, alpha=0.90)
        cv2.rectangle(frame, (banner_x, banner_y), (banner_x + banner_w, banner_y + banner_h), border_color, 3)

        # Chữ Banner chính
        (tw1, th1), _ = cv2.getTextSize(title, self.font, 0.95, 2)
        tx1 = banner_x + (banner_w - tw1) // 2
        cv2.putText(frame, title, (tx1, banner_y + 60), self.font, 0.95, COLOR_TEXT_WHITE, 3, cv2.LINE_AA)

        # Dòng phụ chú hoặc cảnh báo món thiếu
        (tw2, th2), _ = cv2.getTextSize(sub, self.font, 0.70, 2)
        tx2 = banner_x + (banner_w - tw2) // 2
        text_color = (255, 255, 255) if status == "PASS" else (100, 255, 255)
        cv2.putText(frame, sub, (tx2, banner_y + 115), self.font, 0.70, text_color, 2, cv2.LINE_AA)
