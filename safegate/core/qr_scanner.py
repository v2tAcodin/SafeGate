"""
QR Code Scanner for SafeGate
Quét mã QR trên thẻ nhân viên trước khi tiến hành kiểm tra PPE:
- Sử dụng cv2.QRCodeDetector (tích hợp sẵn trong OpenCV, không cần cài zbar.dll).
- Nhận diện mã nhân viên (Staff ID), kiểm tra cơ sở dữ liệu.
- Vẽ khung căn chỉnh quét trực quan trên màn hình.
"""
import cv2
import numpy as np
import json
import time
from typing import Optional, Tuple, Dict, Any
from safegate.database.db_manager import DatabaseManager

class QRScanner:
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.detector = cv2.QRCodeDetector()
        self.db = db_manager or DatabaseManager()
        self.last_scanned_code: Optional[str] = None
        self.last_scan_time: float = 0.0
        self.cooldown_sec: float = 2.0  # Chống quét lặp lại quá nhanh

    def extract_employee_code(self, raw_data: str) -> str:
        """
        Trích xuất mã nhân viên từ nội dung QR:
        Hỗ trợ các định dạng:
        1. Chuỗi trực tiếp: 'NV-1001'
        2. Tiền tố: 'SAFEGATE:NV-1001'
        3. Chuỗi JSON: {"code": "NV-1001", ...}
        4. URL tham số: https://safegate.internal/verify?id=NV-1001
        """
        raw_data = raw_data.strip()
        if not raw_data:
            return ""

        # JSON
        if raw_data.startswith("{") and raw_data.endswith("}"):
            try:
                data_dict = json.loads(raw_data)
                return str(data_dict.get("code") or data_dict.get("id") or "").strip()
            except Exception:
                pass

        # Tiền tố SAFEGATE:
        if raw_data.upper().startswith("SAFEGATE:"):
            return raw_data.split(":", 1)[1].strip()

        # URL chứa id=
        if "id=" in raw_data:
            parts = raw_data.split("id=")
            return parts[1].split("&")[0].strip()

        return raw_data

    def scan_frame(self, frame: np.ndarray) -> Tuple[Optional[Dict[str, Any]], Optional[np.ndarray]]:
        """
        Quét mã QR từ frame camera:
        Return: (employee_dict, qr_points_array)
        - employee_dict: Thông tin nhân viên từ Database (hoặc tạo tạm nếu là mã mới)
        - qr_points_array: Tọa độ 4 đỉnh của mã QR để vẽ hiệu ứng
        """
        if frame is None:
            return None, None

        # Chuyển grayscale để tăng độ tương phản đọc QR
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Nhận diện QR
        data, points, _ = self.detector.detectAndDecode(gray)

        if not data or points is None or len(points) == 0:
            return None, None

        code = self.extract_employee_code(data)
        if not code:
            return None, points

        # Kiểm tra cooldown để không kích hoạt liên tục trong vài frame kế nhau
        now = time.time()
        if code == self.last_scanned_code and (now - self.last_scan_time) < self.cooldown_sec:
            return None, points

        self.last_scanned_code = code
        self.last_scan_time = now

        # Tìm trong cơ sở dữ liệu
        employee = self.db.get_employee_by_code(code)
        if not employee:
            # Nếu chưa có trong DB, vẫn tạo profile hợp lệ với mã vừa quét để test linh hoạt
            employee = {
                "employee_code": code,
                "full_name": f"Khách / Thợ #{code}",
                "department": "Khách vãng lai",
                "role": "Chưa định danh"
            }

        return employee, points
