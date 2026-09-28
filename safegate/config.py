"""
SafeGate Configuration Module
Cấu hình thông số hệ thống kiểm tra đồ bảo hộ lao động (PPE)
"""
from pathlib import Path

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Database
DB_PATH = BASE_DIR / "database" / "safegate.db"

# Model paths
MODELS_DIR = BASE_DIR / "models"
DEFAULT_MODEL_NAME = "yolov8n.pt"  # Pre-trained gốc hoặc custom model
CUSTOM_MODEL_PATH = MODELS_DIR / "safegate_best.pt"
ONNX_MODEL_PATH = MODELS_DIR / "safegate.onnx"

# Danh sách class nhận diện cần thiết
# 0: person, 1: helmet, 2: vest (hoặc ánh xạ theo dataset Roboflow / SHWD / CHV)
TARGET_CLASSES = {
    "person": ["person", "worker", "human"],
    "helmet": ["helmet", "hard-hat", "hardhat", "safety_helmet"],
    "vest": ["vest", "safety_vest", "reflective_vest", "hi-viz-vest"]
}

# Ngưỡng nhận diện YOLO
CONF_THRESHOLD = 0.40
IOU_THRESHOLD = 0.45

# Luật hình học (Geometric Rules)
# Tỷ lệ vị trí so với chiều cao bounding box của Person:
# - Phần đầu: 0% -> 35% chiều cao của người
HELMET_HEAD_ZONE_MAX = 0.38
# - Phần thân: 20% -> 80% chiều cao của người
VEST_TORSO_ZONE_MIN = 0.20
VEST_TORSO_ZONE_MAX = 0.85
# Sai số biên ngang (horizontal tolerance)
HORIZONTAL_TOLERANCE = 0.20  # Cho phép lọt ngoài biên người tối đa 20% width

# Voting đa khung hình (Multi-frame voting)
VOTING_WINDOW_SIZE = 10       # Cửa sổ xét 10 frame gần nhất
REQUIRED_PASS_FRAMES = 8     # Tối thiểu 8/10 frame hợp lệ để kích hoạt PASS
MAX_CHECK_TIMEOUT_SEC = 7.0  # Thời gian tối đa cho 1 lượt check (sau đó chốt kết quả nếu chưa đủ 8/10)
RESULT_DISPLAY_SEC = 3.0     # Thời gian giữ màn hình kết quả PASS/FAIL trước khi reset

# Camera
DEFAULT_CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30
