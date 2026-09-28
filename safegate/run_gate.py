"""
SafeGate - Realtime Camera Gate Runner
Ứng dụng kiểm tra cổng thời gian thực chạy trực tiếp với Webcam laptop:
- Phím 'Q' hoặc ESC: Thoát chương trình
- Phím SPACE: Bắt đầu kiểm tra nhanh (bỏ qua quét QR)
- Phím 'R': Đặt lại (Reset) về trạng thái Chờ quét thẻ
- Phím 'H': Bật/Tắt mô phỏng Mũ bảo hộ (Test kịch bản có/thiếu mũ)
- Phím 'V': Bật/Tắt mô phỏng Áo phản quang (Test kịch bản có/thiếu áo)
- Phím 'T': Mô phỏng cầm mũ trên tay (Test luật hình học phát hiện gian lận)
"""
import cv2
import argparse
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from pathlib import Path

# Thêm đường dẫn gốc để chạy trực tiếp
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from safegate.config import DEFAULT_CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from safegate.core.pipeline import SafeGatePipeline, GateState
from safegate.core.geometric_rules import DetectionBox

def main():
    parser = argparse.ArgumentParser(description="SafeGate Realtime PPE Gate-Check")
    parser.add_argument("--camera", type=int, default=DEFAULT_CAMERA_INDEX, help="Camera index (mặc định 0)")
    parser.add_argument("--video", type=str, default=None, help="Đường dẫn file video test (thay thế webcam)")
    parser.add_argument("--onnx", action="store_true", help="Sử dụng ONNX Runtime tăng tốc")
    parser.add_argument("--model", type=str, default=None, help="Đường dẫn file trọng số model custom")
    args = parser.parse_args()

    print("=" * 60)
    print("   SAFEGATE - CỔNG KIỂM TRA ĐỒ BẢO HỘ LAO ĐỘNG (PPE) BẰNG AI")
    print("=" * 60)
    print("Đang khởi tạo hệ thống...")

    # Khởi tạo Pipeline
    pipeline = SafeGatePipeline()

    # Mở Camera hoặc Video
    source = args.video if args.video else args.camera
    cap = cv2.VideoCapture(source)

    if not args.video:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[SafeGate Error] Không thể kết nối đến camera/nguồn video: {source}")
        print("Gợi ý: Kiểm tra quyền truy cập webcam trên Windows hoặc truyền đường dẫn video qua --video")
        return

    window_name = "SafeGate - AI PPE Inspection System"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1100, 680)

    print("\n[HỆ THỐNG ĐÃ SẴN SÀNG]")
    print("- Đưa thẻ nhân viên (Mã QR) vào vùng ngắm mục tiêu ở giữa màn hình")
    print("- Hoặc nhấn [SPACE] để kích hoạt kiểm tra nhanh công nhân mẫu")
    print("- Nhấn phím 'H' / 'V' để test kịch bản thiếu/đủ Mũ và Áo")
    print("- Nhấn 'Q' để thoát\n")

    holding_helmet_test = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if args.video:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Lặp video
                    continue
                else:
                    print("[SafeGate] Mất tín hiệu camera...")
                    break

            # Xử lý frame qua Pipeline
            processed_frame = pipeline.process_frame(frame)

            # Vẽ thanh hướng dẫn phím tắt ở đáy khung hình
            h, w = processed_frame.shape[:2]
            footer_text = "[SPACE]: Check ngay  |  [H]: Bat/Tat Mu  |  [V]: Bat/Tat Ao  |  [T]: Test Cam Tay  |  [R]: Reset  |  [Q]: Thoat"
            cv2.putText(processed_frame, footer_text, (20, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

            # Hiển thị cửa sổ
            cv2.imshow(window_name, processed_frame)

            # Xử lý phím bấm điều khiển
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), ord('Q'), 27):  # ESC or Q
                break
            elif key == ord(' '):  # SPACE
                print("[Action] Kích hoạt kiểm tra thủ công nhanh!")
                pipeline.trigger_manual_check("NV-1001")
            elif key in (ord('r'), ord('R')):
                print("[Action] Đặt lại hệ thống về trạng thái Chờ quét thẻ.")
                pipeline.reset_to_scan_state()
            elif key in (ord('h'), ord('H')):
                pipeline.detector.simulation_helmet = not pipeline.detector.simulation_helmet
                st = "BẬT" if pipeline.detector.simulation_helmet else "TẮT (Thiếu mũ)"
                print(f"[Test Toggle] Mũ bảo hộ: {st}")
            elif key in (ord('v'), ord('V')):
                pipeline.detector.simulation_vest = not pipeline.detector.simulation_vest
                st = "BẬT" if pipeline.detector.simulation_vest else "TẮT (Thiếu áo)"
                print(f"[Test Toggle] Áo phản quang: {st}")
            elif key in (ord('t'), ord('T')):
                holding_helmet_test = not holding_helmet_test
                st = "CẦM TAY (Gian lận)" if holding_helmet_test else "ĐỘI TRÊN ĐẦU"
                print(f"[Test Toggle] Vị trí mũ: {st}")

    except KeyboardInterrupt:
        print("\n[SafeGate] Đang dừng chương trình...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[SafeGate] Đã giải phóng camera và đóng cửa sổ thành công.")

if __name__ == "__main__":
    main()
