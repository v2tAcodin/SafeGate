"""
SafeGate Unit Test Suite
Kiểm thử tự động các thành phần quan trọng theo chuẩn CNPM (Ch08 - Testing):
1. Test Luật hình học (Geometric Rules) & Chống gian lận cầm mũ trên tay.
2. Test Bộ lọc Voting đa khung hình (8/10 frames).
3. Test Cơ sở dữ liệu SQLite & Tiêu chí bảo vệ quyền riêng tư (Không lưu ảnh).
"""
import sys
from pathlib import Path
import unittest

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from safegate.core.geometric_rules import GeometricRuleValidator, DetectionBox
from safegate.core.frame_voting import MultiFrameVoter
from safegate.database.db_manager import DatabaseManager

class TestSafeGateCore(unittest.TestCase):

    def setUp(self):
        self.validator = GeometricRuleValidator()
        self.voter = MultiFrameVoter(window_size=10, required_pass_count=8, max_timeout_sec=2.0)
        # Sử dụng DB tạm trong bộ nhớ
        self.db = DatabaseManager(db_path=BASE_DIR / "database" / "test_safegate.db")

    def test_geometric_rules_compliant(self):
        """Kiểm thử trường hợp ĐẠT: Mũ đội trên đầu, Áo mặc trên thân"""
        # Giả lập người kích thước 300x600 tại (100, 100) đến (400, 700)
        person = DetectionBox(class_name="person", confidence=0.9, x1=100, y1=100, x2=400, y2=700)
        # Mũ bảo hộ trên đỉnh đầu (y từ 90 đến 220) -> relative_y ~ 0.09 (<= 0.38)
        helmet = DetectionBox(class_name="helmet", confidence=0.88, x1=180, y1=90, x2=320, y2=220)
        # Áo phản quang ở thân (y từ 250 đến 550) -> relative_y ~ 0.50
        vest = DetectionBox(class_name="vest", confidence=0.85, x1=130, y1=250, x2=370, y2=550)

        eval_res = self.validator.evaluate_frame([person, helmet, vest], 800, 800)
        
        self.assertTrue(eval_res.has_person)
        self.assertTrue(eval_res.helmet_on_head)
        self.assertTrue(eval_res.vest_on_torso)
        self.assertFalse(eval_res.is_holding_helmet)
        self.assertTrue(eval_res.is_compliant)
        self.assertEqual(len(eval_res.missing_items), 0)

    def test_geometric_rules_holding_helmet(self):
        """Kiểm thử trường hợp GIAN LẬN: Cầm mũ trên tay thay vì đội trên đầu"""
        person = DetectionBox(class_name="person", confidence=0.9, x1=100, y1=100, x2=400, y2=700)
        # Mũ ở ngang hông/tay (y từ 450 đến 550) -> relative_y ~ 0.67 (> 0.40)
        held_helmet = DetectionBox(class_name="helmet", confidence=0.88, x1=120, y1=450, x2=240, y2=550)
        vest = DetectionBox(class_name="vest", confidence=0.85, x1=130, y1=250, x2=370, y2=550)

        eval_res = self.validator.evaluate_frame([person, held_helmet, vest], 800, 800)

        self.assertFalse(eval_res.helmet_on_head)
        self.assertTrue(eval_res.is_holding_helmet)
        self.assertFalse(eval_res.is_compliant)
        self.assertTrue(any("cầm tay" in m.lower() for m in eval_res.missing_items))

    def test_multi_frame_voting_pass(self):
        """Kiểm thử voting đạt 8/10 frame -> Kích hoạt trạng thái PASS"""
        self.voter.start_session()
        
        person = DetectionBox(class_name="person", confidence=0.9, x1=100, y1=100, x2=400, y2=700)
        helmet = DetectionBox(class_name="helmet", confidence=0.88, x1=180, y1=90, x2=320, y2=220)
        vest = DetectionBox(class_name="vest", confidence=0.85, x1=130, y1=250, x2=370, y2=550)
        compliant_eval = self.validator.evaluate_frame([person, helmet, vest], 800, 800)

        # Nạp 8 frame hợp lệ liên tiếp
        status = "CHECKING"
        for i in range(8):
            status, ratio, missing = self.voter.add_frame(compliant_eval)
        
        self.assertEqual(status, "PASS")
        self.assertEqual(len(missing), 0)

    def test_database_privacy_no_images(self):
        """Kiểm tra SQLite lưu đầy đủ thông tin nhưng TUYỆT ĐỐI không lưu ảnh / binary blob"""
        log_id = self.db.log_access(
            employee_code="NV-TEST-99",
            employee_name="Công nhân Thử Nghiệm",
            department="Ban An Toàn",
            status="PASS",
            missing_items=[],
            vote_score="8/10",
            duration=1.5
        )
        self.assertGreater(log_id, 0)

        logs = self.db.get_logs(limit=1, search_keyword="NV-TEST-99")
        self.assertEqual(len(logs), 1)
        log = logs[0]
        self.assertEqual(log["employee_code"], "NV-TEST-99")
        self.assertEqual(log["status"], "PASS")

        # Kiểm tra cấu trúc các cột trong bảng access_logs: không có cột image_path hay photo blob
        columns = list(log.keys())
        for col in columns:
            self.assertNotIn("image", col.lower())
            self.assertNotIn("photo", col.lower())
            self.assertNotIn("pic", col.lower())

    def tearDown(self):
        # Dọn dẹp test db nếu cần
        pass

if __name__ == "__main__":
    unittest.main()
