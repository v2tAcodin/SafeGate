"""
Multi-Frame Voting Filter for SafeGate
Bộ lọc voting đa khung hình:
- Tránh hiện tượng nhấp nháy (flickering / false positive / false negative) của mô hình AI.
- Chỉ công nhận PASS khi đạt ít nhất 8/10 frame liên tiếp (hoặc trong cửa sổ trượt 10 frame gần nhất).
- Quản lý trạng thái và thời gian kiểm tra (timeout).
"""
import time
from collections import deque
from typing import List, Tuple, Optional, Dict
from safegate.config import VOTING_WINDOW_SIZE, REQUIRED_PASS_FRAMES, MAX_CHECK_TIMEOUT_SEC
from safegate.core.geometric_rules import EvaluationResult

class MultiFrameVoter:
    def __init__(self,
                 window_size: int = VOTING_WINDOW_SIZE,
                 required_pass_count: int = REQUIRED_PASS_FRAMES,
                 max_timeout_sec: float = MAX_CHECK_TIMEOUT_SEC):
        self.window_size = window_size
        self.required_pass_count = required_pass_count
        self.max_timeout_sec = max_timeout_sec

        self.history: deque = deque(maxlen=window_size)
        self.missing_items_history: deque = deque(maxlen=window_size)
        
        self.start_time: Optional[float] = None
        self.consecutive_pass: int = 0
        self.max_consecutive_pass: int = 0

    def start_session(self):
        """Bắt đầu phiên kiểm tra mới cho một nhân viên"""
        self.history.clear()
        self.missing_items_history.clear()
        self.start_time = time.time()
        self.consecutive_pass = 0
        self.max_consecutive_pass = 0

    def reset(self):
        """Khôi phục về trạng thái chờ"""
        self.history.clear()
        self.missing_items_history.clear()
        self.start_time = None
        self.consecutive_pass = 0
        self.max_consecutive_pass = 0

    def add_frame(self, evaluation: EvaluationResult) -> Tuple[str, float, List[str]]:
        """
        Nạp kết quả đánh giá của frame hiện tại vào bộ đệm.
        Return: (status: 'CHECKING' | 'PASS' | 'FAIL', progress_ratio: float, persistent_missing_items: list)
        """
        if self.start_time is None:
            self.start_time = time.time()

        is_frame_pass = evaluation.is_compliant
        self.history.append(is_frame_pass)
        self.missing_items_history.append(evaluation.missing_items)

        # Cập nhật số frame pass liên tiếp
        if is_frame_pass:
            self.consecutive_pass += 1
            if self.consecutive_pass > self.max_consecutive_pass:
                self.max_consecutive_pass = self.consecutive_pass
        else:
            self.consecutive_pass = 0

        # Số frame pass trong cửa sổ trượt 10 frame gần nhất
        pass_in_window = sum(1 for p in self.history if p)
        total_in_window = len(self.history)

        # Tiến độ đạt được (ví dụ: 8/10 -> 0.8)
        progress_ratio = min(1.0, max(pass_in_window, self.consecutive_pass) / float(self.required_pass_count))

        # Điều kiện PASS: Đạt ít nhất 8/10 frame trong window HOẶC 8 frame liên tiếp
        if (pass_in_window >= self.required_pass_count and total_in_window >= self.required_pass_count) or (self.consecutive_pass >= self.required_pass_count):
            return "PASS", 1.0, []

        # Kiểm tra quá thời gian kiểm tra (Timeout)
        elapsed = time.time() - self.start_time
        if elapsed >= self.max_timeout_sec:
            # Hết thời gian mà chưa đủ 8/10 frame -> Kết luận FAIL
            common_missing = self._get_most_common_missing()
            return "FAIL", progress_ratio, common_missing

        return "CHECKING", progress_ratio, self._get_most_common_missing()

    def _get_most_common_missing(self) -> List[str]:
        """Tổng hợp các món thiếu phổ biến nhất từ các frame không đạt trong window"""
        missing_counts: Dict[str, int] = {}
        for items in self.missing_items_history:
            for item in items:
                missing_counts[item] = missing_counts.get(item, 0) + 1

        # Trả về các món thiếu xuất hiện ở >= 30% số frame lỗi
        threshold = max(1, len(self.missing_items_history) * 0.3)
        result = [item for item, cnt in missing_counts.items() if cnt >= threshold]
        
        if not result and missing_counts:
            result = list(missing_counts.keys())
        return result

    @property
    def current_score_str(self) -> str:
        """Chuỗi hiển thị tỷ lệ frame pass hiện tại, ví dụ '8/10'"""
        pass_count = sum(1 for p in self.history if p)
        return f"{pass_count}/{len(self.history)}" if self.history else "0/10"

    @property
    def elapsed_time(self) -> float:
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
