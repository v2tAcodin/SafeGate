"""
ONNX Exporter and Benchmark Utility for SafeGate
Tối ưu hóa và kiểm thử hiệu năng mô hình trên laptop:
- Export mô hình PyTorch YOLO nano sang ONNX.
- Lượng tử hóa mô hình (INT8 Quantization qua ONNX Runtime).
- Benchmark độ trễ (Latency ms), tốc độ khung hình (FPS), kích thước mô hình (MB).
"""
import time
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

class ModelOptimizer:
    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else Path(__file__).resolve().parent.parent / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def export_onnx(self, pt_model_path: str = "yolov8n.pt", imgsz: int = 640) -> Optional[str]:
        """
        Export mô hình YOLO (.pt) sang định dạng ONNX
        """
        try:
            from ultralytics import YOLO
            print(f"[SafeGate Optimizer] Đang export {pt_model_path} sang ONNX...")
            model = YOLO(pt_model_path)
            exported_path = model.export(format="onnx", imgsz=imgsz, dynamic=False, simplify=True)
            print(f"[SafeGate Optimizer] Export thành công: {exported_path}")
            return exported_path
        except Exception as e:
            print(f"[SafeGate Optimizer] Lỗi khi export ONNX: {e}")
            return None

    def quantize_int8(self, onnx_model_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Lượng tử hóa mô hình ONNX sang INT8 (giảm 50-70% dung lượng, tăng tốc CPU)
        """
        onnx_file = Path(onnx_model_path)
        if not onnx_file.exists():
            print(f"[SafeGate Optimizer] File không tồn tại: {onnx_model_path}")
            return None

        if output_path is None:
            output_path = str(onnx_file.parent / f"{onnx_file.stem}_int8.onnx")

        try:
            from onnxruntime.quantization import quantize_dynamic, QuantType
            print(f"[SafeGate Optimizer] Bắt đầu lượng tử hóa INT8: {onnx_model_path} -> {output_path}")
            quantize_dynamic(
                model_input=str(onnx_file),
                model_output=str(output_path),
                weight_type=QuantType.QUInt8
            )
            print(f"[SafeGate Optimizer] Lượng tử hóa INT8 thành công!")
            return output_path
        except Exception as e:
            print(f"[SafeGate Optimizer] Lỗi khi lượng tử hóa INT8: {e}")
            return None

    def benchmark(self, model_target: str = "yolov8n.pt", num_runs: int = 40,
                  imgsz: int = 640) -> Dict[str, Any]:
        """
        Đo lường hiệu năng thực tế (Latency ms, FPS, File size MB) trên CPU laptop
        """
        print(f"[SafeGate Benchmark] Bắt đầu benchmark cho {model_target} ({num_runs} vòng lặp)...")
        
        file_path = Path(model_target)
        file_size_mb = (file_path.stat().st_size / (1024 * 1024)) if file_path.exists() else 0.0

        # Tạo dummy input frame (BGR)
        dummy_frame = np.random.randint(0, 255, (imgsz, imgsz, 3), dtype=np.uint8)

        latencies = []

        if str(model_target).endswith(".onnx"):
            # Benchmark ONNX Runtime
            import onnxruntime as ort
            session = ort.InferenceSession(str(model_target), providers=["CPUExecutionProvider"])
            input_name = session.get_inputs()[0].name
            
            # Chuẩn bị tensor (1, 3, H, W) float32 [0..1]
            blob = cv2_preprocess(dummy_frame, imgsz)

            # Warmup 5 vòng
            for _ in range(5):
                _ = session.run(None, {input_name: blob})

            for _ in range(num_runs):
                t0 = time.perf_counter()
                _ = session.run(None, {input_name: blob})
                latencies.append((time.perf_counter() - t0) * 1000.0)

        else:
            # Benchmark Ultralytics PyTorch
            from ultralytics import YOLO
            model = YOLO(model_target)

            # Warmup
            for _ in range(5):
                _ = model.predict(dummy_frame, verbose=False, device="cpu")

            for _ in range(num_runs):
                t0 = time.perf_counter()
                _ = model.predict(dummy_frame, verbose=False, device="cpu")
                latencies.append((time.perf_counter() - t0) * 1000.0)

        avg_latency = float(np.mean(latencies))
        min_latency = float(np.min(latencies))
        max_latency = float(np.max(latencies))
        fps = round(1000.0 / avg_latency, 1) if avg_latency > 0 else 0.0

        results = {
            "model": str(model_target),
            "file_size_mb": round(file_size_mb, 2),
            "num_runs": num_runs,
            "avg_latency_ms": round(avg_latency, 2),
            "min_latency_ms": round(min_latency, 2),
            "max_latency_ms": round(max_latency, 2),
            "estimated_fps": fps
        }

        print(f"[SafeGate Benchmark Kết quả]: {results}")
        return results

def cv2_preprocess(img: np.ndarray, size: int) -> np.ndarray:
    """Preprocess frame cho ONNX input tensor: (1, 3, size, size)"""
    import cv2
    resized = cv2.resize(img, (size, size))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    normalized = rgb.astype(np.float32) / 255.0
    transposed = np.transpose(normalized, (2, 0, 1))
    return np.expand_dims(transposed, axis=0)
