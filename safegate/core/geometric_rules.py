"""
Geometric Rules Validator for SafeGate
Kiểm tra tính hợp lệ về mặt không gian hình học của đồ bảo hộ (PPE):
- Mũ bảo hộ PHẢI đội trên đầu (1/3 phần trên của cơ thể).
- Áo phản quang PHẢI mặc ở phần thân (khoảng 20% - 85% chiều cao).
- Ngăn chặn và phát hiện trường hợp gian lận: Cầm mũ trên tay hoặc treo ở hông.
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from safegate.config import (
    HELMET_HEAD_ZONE_MAX,
    VEST_TORSO_ZONE_MIN,
    VEST_TORSO_ZONE_MAX,
    HORIZONTAL_TOLERANCE
)

@dataclass
class DetectionBox:
    class_name: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center_x(self) -> float:
        return (self.x1 + self.x2) / 2.0

    @property
    def center_y(self) -> float:
        return (self.y1 + self.y2) / 2.0

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class EvaluationResult:
    has_person: bool = False
    has_helmet: bool = False
    has_vest: bool = False
    helmet_on_head: bool = False
    vest_on_torso: bool = False
    is_holding_helmet: bool = False
    is_compliant: bool = False
    missing_items: List[str] = None
    primary_person: Optional[DetectionBox] = None
    matched_helmet: Optional[DetectionBox] = None
    matched_vest: Optional[DetectionBox] = None
    detail_message: str = ""

    def __post_init__(self):
        if self.missing_items is None:
            self.missing_items = []


class GeometricRuleValidator:
    def __init__(self,
                 head_zone_max: float = HELMET_HEAD_ZONE_MAX,
                 torso_zone_min: float = VEST_TORSO_ZONE_MIN,
                 torso_zone_max: float = VEST_TORSO_ZONE_MAX,
                 horiz_tolerance: float = HORIZONTAL_TOLERANCE):
        self.head_zone_max = head_zone_max
        self.torso_zone_min = torso_zone_min
        self.torso_zone_max = torso_zone_max
        self.horiz_tolerance = horiz_tolerance

    def find_primary_person(self, detections: List[DetectionBox], frame_width: int, frame_height: int) -> Optional[DetectionBox]:
        """
        Xác định công nhân chính đang đứng trước cổng kiểm tra:
        - Ưu tiên người có diện tích bounding box lớn nhất và gần tâm màn hình nhất.
        """
        people = [d for d in detections if d.class_name == "person"]
        if not people:
            return None

        center_x = frame_width / 2.0
        center_y = frame_height / 2.0

        def score_person(p: DetectionBox):
            # Điểm = Diện tích / (1 + khoảng cách đến tâm)
            dist_sq = (p.center_x - center_x) ** 2 + (p.center_y - center_y) ** 2
            return p.area / (1.0 + 0.001 * dist_sq)

        return max(people, key=score_person)

    def validate_helmet_position(self, person: DetectionBox, helmet: DetectionBox) -> Tuple[bool, bool]:
        """
        Kiểm tra mũ bảo hộ:
        - Return: (helmet_on_head: bool, is_holding_helmet: bool)
        """
        p_h = person.height
        p_w = person.width
        if p_h <= 0 or p_w <= 0:
            return False, False

        # Kiểm tra theo trục ngang: mũ phải nằm trong phạm vi người (cộng sai số)
        horiz_margin = p_w * self.horiz_tolerance
        in_horiz_bound = (person.x1 - horiz_margin) <= helmet.center_x <= (person.x2 + horiz_margin)

        # Tính vị trí tương đối của tâm mũ so với đỉnh đầu người
        # 0.0 = Đỉnh đầu người (person.y1), 1.0 = Đáy chân người (person.y2)
        relative_y = (helmet.center_y - person.y1) / p_h

        # Mũ đội trên đầu nếu tâm mũ nằm từ khoảng -10% (trồi lên trên đỉnh đầu) đến head_zone_max (khoảng 38% đầu/cổ)
        if in_horiz_bound and (-0.15 <= relative_y <= self.head_zone_max):
            return True, False

        # Nếu mũ nằm ở vùng tay/hông (relative_y > 0.40) -> Gian lận cầm mũ trên tay
        if relative_y > 0.40:
            return False, True

        return False, False

    def validate_vest_position(self, person: DetectionBox, vest: DetectionBox) -> bool:
        """
        Kiểm tra áo phản quang:
        - Áo phải bao phủ vùng thân (khoảng 20% đến 85% chiều cao của người).
        """
        p_h = person.height
        p_w = person.width
        if p_h <= 0 or p_w <= 0:
            return False

        horiz_margin = p_w * self.horiz_tolerance
        in_horiz_bound = (person.x1 - horiz_margin) <= vest.center_x <= (person.x2 + horiz_margin)

        relative_y = (vest.center_y - person.y1) / p_h

        if in_horiz_bound and (self.torso_zone_min <= relative_y <= self.torso_zone_max):
            return True

        return False

    def evaluate_frame(self, detections: List[DetectionBox], frame_width: int, frame_height: int) -> EvaluationResult:
        """
        Đánh giá toàn diện 1 frame ảnh từ webcam:
        1. Tìm công nhân chính (person)
        2. Ghép cặp và kiểm tra vị trí Mũ (Helmet)
        3. Ghép cặp và kiểm tra vị trí Áo (Vest)
        4. Kết luận PASS / FAIL cho frame này
        """
        result = EvaluationResult()

        primary_person = self.find_primary_person(detections, frame_width, frame_height)
        if not primary_person:
            result.detail_message = "Không phát hiện người trước cổng kiểm tra"
            return result

        result.has_person = True
        result.primary_person = primary_person

        # Lọc danh sách helmet và vest
        helmets = [d for d in detections if d.class_name == "helmet"]
        vests = [d for d in detections if d.class_name == "vest"]

        # Kiểm tra mũ
        for h in helmets:
            on_head, holding = self.validate_helmet_position(primary_person, h)
            if on_head:
                result.has_helmet = True
                result.helmet_on_head = True
                result.matched_helmet = h
                break
            elif holding:
                result.has_helmet = True
                result.is_holding_helmet = True
                result.matched_helmet = h

        # Kiểm tra áo
        for v in vests:
            if self.validate_vest_position(primary_person, v):
                result.has_vest = True
                result.vest_on_torso = True
                result.matched_vest = v
                break

        # Xác định các món còn thiếu hoặc vi phạm
        missing = []
        if not result.helmet_on_head:
            if result.is_holding_helmet:
                missing.append("Mũ bảo hộ (Đang cầm tay, chưa đội)")
            else:
                missing.append("Mũ bảo hộ")
        
        if not result.vest_on_torso:
            missing.append("Áo phản quang")

        result.missing_items = missing
        result.is_compliant = (result.helmet_on_head and result.vest_on_torso)

        if result.is_compliant:
            result.detail_message = "Đầy đủ trang thiết bị bảo hộ (Đúng vị trí quy chuẩn)"
        else:
            result.detail_message = f"Chưa đạt yêu cầu: Thiếu {', '.join(missing)}"

        return result
