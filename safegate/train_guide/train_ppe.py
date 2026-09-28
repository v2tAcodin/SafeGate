"""
SafeGate - Free Model Training Script for Google Colab / Kaggle (GPU T4)
Huấn luyện YOLOv8 nano trên tập dữ liệu đồ bảo hộ PPE (person, helmet, vest):
- Hoàn toàn miễn phí trên Colab/Kaggle.
- Thời gian train: ~15 - 25 phút.
- Tự động xuất model safegate_best.pt và safegate.onnx.
"""

def generate_colab_instructions():
    code = '''# ==============================================================================
# BƯỚC 1: CÀI ĐẶT THƯ VIỆN ULTRALYTICS TRÊN COLAB / KAGGLE
# ==============================================================================
!pip install ultralytics roboflow

# ==============================================================================
# BƯỚC 2: TẢI DATASET TỪ ROBOFLOW UNIVERSE HOẶC SHWD
# (Ví dụ: Dataset "Hard Hat and Safety Vest Workers" trên Roboflow Universe)
# ==============================================================================
from roboflow import Roboflow
# Đăng ký tài khoản miễn phí tại roboflow.com và lấy API key
# rf = Roboflow(api_key="YOUR_ROBOFLOW_API_KEY")
# project = rf.workspace("roboflow-universe-projects").project("construction-site-safety")
# dataset = project.version(1).download("yolov8")

# Hoặc nếu bạn đã tải file data.yaml và thư mục images/labels lên Google Drive:
# data_yaml_path = "/content/drive/MyDrive/safegate_dataset/data.yaml"

# ==============================================================================
# BƯỚC 3: HUẤN LUYỆN YOLOV8 NANO VỚI GPU T4
# ==============================================================================
from ultralytics import YOLO

# Khởi tạo YOLOv8 nano (nhẹ nhất, tối ưu chạy trên laptop)
model = YOLO("yolov8n.pt")

# Bắt đầu train
results = model.train(
    data="data.yaml",       # Đường dẫn tới file config dataset
    epochs=50,              # 50 epochs (đủ hội tụ tốt cho bài toán PPE)
    imgsz=640,
    batch=16,
    device=0,               # Dùng GPU T4 miễn phí
    name="safegate_ppe",
    plots=True
)

# ==============================================================================
# BƯỚC 4: ĐÁNH GIÁ (VALIDATE) VÀ XUẤT ONNX TỐI ƯU
# ==============================================================================
# Đánh giá mAP50 và mAP50-95 trên tập validation độc lập
metrics = model.val()
print("mAP50-95:", metrics.box.map)
print("mAP50:", metrics.box.map50)

# Export sang ONNX để mang về laptop chạy siêu nhanh bằng ONNX Runtime
onnx_path = model.export(format="onnx", imgsz=640, dynamic=False, simplify=True)
print("Đã export ONNX thành công:", onnx_path)

# Tải file weights 'best.pt' và 'best.onnx' về máy tính cá nhân đặt vào thư mục safegate/models/!
'''
    return code

if __name__ == "__main__":
    print("=" * 60)
    print("SafeGate PPE Training Guide")
    print("=" * 60)
    print(generate_colab_instructions())
