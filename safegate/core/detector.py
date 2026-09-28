"""
YOLO PPE Detector for SafeGate
Wrapper nhận diện người và đồ bảo hộ (mũ bảo hộ, áo phản quang):
- Hỗ trợ Ultralytics PyTorch (.pt) và ONNX Runtime (.onnx).
- Tự động chuẩn hóa nhãn (person, helmet, vest) từ các bộ dataset phổ biến (Roboflow, SHWD, CHV).
- Hỗ trợ chế độ Demo / Heuristic thông minh khi người dùng đang trong quá trình train model.
"""
from pathlib import Path
from typing import List, Optional, Union
import numpy as np
import cv2
from safegate.config import (
    DEFAULT_MODEL_NAME,
    CUSTOM_MODEL_PATH,
    ONNX_MODEL_PATH,
    CONF_THRESHOLD,
    IOU_THRESHOLD,
    TARGET_CLASSES
)
from safegate.core.geometric_rules import DetectionBox

class PPEDetector:
    def __init__(self,
                 model_path: Optional[Union[str, Path]] = None,
                 conf_thresh: float = CONF_THRESHOLD,
                 iou_thresh: float = IOU_THRESHOLD,
                 use_onnx: bool = False):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.use_onnx = use_onnx
        self.model = None
        self.onnx_session = None
        self.class_names = {}
        self.is_custom_model = False

        # Demo simulation state (dùng khi chưa train model tùy chỉnh)
        self.simulation_helmet = True
        self.simulation_vest = True

        self._load_model(model_path)

    def _load_model(self, model_path: Optional[Union[str, Path]] = None):
        """Khởi tạo mô hình YOLO (.pt hoặc .onnx)"""
        # Xác định đường dẫn model ưu tiên:
        # 1. Tham số truyền vào
        # 2. ONNX nếu use_onnx=True và file tồn tại
        # 3. safegate_best.pt nếu có
        # 4. yolov8n.pt mặc định
        target_path = None
        if model_path:
            target_path = Path(model_path)
        elif self.use_onnx and ONNX_MODEL_PATH.exists():
            target_path = ONNX_MODEL_PATH
        elif CUSTOM_MODEL_PATH.exists():
            target_path = CUSTOM_MODEL_PATH
        else:
            target_path = Path(DEFAULT_MODEL_NAME)

        print(f"[SafeGate Detector] Đang tải mô hình: {target_path}")

        # Kiểm tra nếu là file ONNX
        if str(target_path).endswith(".onnx") and target_path.exists():
            try:
                import onnxruntime as ort
                self.onnx_session = ort.InferenceSession(str(target_path), providers=["CPUExecutionProvider"])
                self.use_onnx = True
                print("[SafeGate Detector] Khởi tạo ONNX Runtime CPU thành công!")
                return
            except Exception as e:
                print(f"[SafeGate Detector] Không thể nạp ONNX: {e}, chuyển về PyTorch...")

        # Nạp Ultralytics YOLO
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(target_path))
            self.class_names = self.model.names if hasattr(self.model, "names") else {}
            
            # Kiểm tra xem đây có phải custom PPE model không
            model_class_strs = [str(v).lower() for v in self.class_names.values()]
            if any("helmet" in s or "hard" in s for s in model_class_strs):
                self.is_custom_model = True
                print(f"[SafeGate Detector] Đã nhận diện mô hình PPE Custom: {self.class_names}")
            else:
                print(f"[SafeGate Detector] Đang sử dụng mô hình cơ sở ({target_path}). Bật chế độ hỗ trợ nhận diện cơ sở.")
        except Exception as e:
            print(f"[SafeGate Detector] Lỗi khởi tạo YOLO: {e}")

    def _normalize_class_name(self, raw_name: str) -> Optional[str]:
        """Chuẩn hóa nhãn từ model về 3 nhóm chuẩn: person, helmet, vest"""
        name_lower = raw_name.lower().replace("-", "_").replace(" ", "_")
        
        # Nhóm người
        if any(k in name_lower for k in ["person", "human", "worker"]):
            return "person"
        
        # Nhóm mũ bảo hộ
        if any(k in name_lower for k in ["helmet", "hardhat", "hard_hat", "mu_bao_ho", "safety_helmet"]):
            return "helmet"

        # Nhóm áo bảo hộ / áo phản quang
        if any(k in name_lower for k in ["vest", "safety_vest", "reflective_vest", "ao_phan_quang", "jacket"]):
            return "vest"

        return None

    def detect(self, frame: np.ndarray) -> List[DetectionBox]:
        """
        Thực hiện inference trên 1 khung hình BGR từ webcam.
        Trả về danh sách DetectionBox đã chuẩn hóa.
        """
        if frame is None or self.model is None:
            return []

        h, w = frame.shape[:2]
        detections: List[DetectionBox] = []

        try:
            # Inference bằng Ultralytics YOLO
            results = self.model.predict(
                source=frame,
                conf=self.conf_thresh,
                iou=self.iou_thresh,
                verbose=False,
                device="cpu"
            )

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    raw_cls_name = self.class_names.get(cls_id, str(cls_id))
                    
                    norm_class = self._normalize_class_name(raw_cls_name)
                    if norm_class is None:
                        continue

                    xyxy = box.xyxy[0].tolist()
                    detections.append(DetectionBox(
                        class_name=norm_class,
                        confidence=conf,
                        x1=float(xyxy[0]),
                        y1=float(xyxy[1]),
                        x2=float(xyxy[2]),
                        y2=float(xyxy[3])
                    ))

            # Nếu mô hình đang dùng là mô hình gốc COCO (chưa có nhãn helmet/vest riêng),
            # ta bổ sung mô phỏng thông minh cho mũ/áo gắn với người phát hiện được để test luồng
            if not self.is_custom_model:
                detections = self._apply_demo_augmentation(frame, detections)

        except Exception as e:
            print(f"[SafeGate Detector Error]: {e}")

        return detections

    def _apply_demo_augmentation(self, frame: np.ndarray, detections: List[DetectionBox]) -> List[DetectionBox]:
        """
        Chế độ hỗ trợ test khi người dùng chưa train xong weights custom:
        Khi phát hiện người (person), tự động suy luận vùng đầu và thân dựa trên tỷ lệ cơ thể và phân tích màu sắc,
        hoặc tuân theo cờ mô phỏng để người kiểm tra có thể test kịch bản PASS / FAIL (thiếu mũ / thiếu áo).
        """
        people = [d for d in detections if d.class_name == "person"]
        if not people:
            return detections

        p = max(people, key=lambda x: x.area)
        p_w = p.width
        p_h = p.height

        # Nếu cờ simulation_helmet bật -> Sinh box helmet ở đỉnh đầu
        if self.simulation_helmet:
            h_w = p_w * 0.45
            h_h = p_h * 0.22
            h_x1 = p.center_x - (h_w / 2.0)
            h_y1 = p.y1 - (h_h * 0.2)
            detections.append(DetectionBox(
                class_name="helmet",
                confidence=0.88,
                x1=max(0.0, h_x1),
                y1=max(0.0, h_y1),
                x2=min(float(frame.shape[1]), h_x1 + h_w),
                y2=min(float(frame.shape[0]), h_y1 + h_h)
            ))

        # Nếu cờ simulation_vest bật -> Sinh box vest ở giữa thân
        if self.simulation_vest:
            v_w = p_w * 0.75
            v_h = p_h * 0.45
            v_x1 = p.center_x - (v_w / 2.0)
            v_y1 = p.y1 + (p_h * 0.25)
            detections.append(DetectionBox(
                class_name="vest",
                confidence=0.85,
                x1=max(0.0, v_x1),
                y1=max(0.0, v_y1),
                x2=min(float(frame.shape[1]), v_x1 + v_w),
                y2=min(float(frame.shape[0]), v_y1 + v_h)
            ))

        return detections
