"""
SafeGate - Realtime Camera Gate Runner
Ứng dụng kiểm tra cổng thời gian thực chạy trực tiếp với Webcam laptop:
- Tự động chuyển sang Chế độ Giả lập (Virtual Camera Simulator) nếu máy không có webcam!
- Phím 'Q' hoặc ESC: Thoát chương trình
- Phím SPACE: Bắt đầu kiểm tra nhanh
- Phím 'S': Giả lập đưa thẻ nhân viên QR vào khung ngắm
- Phím 'R': Đặt lại (Reset) về trạng thái Chờ quét thẻ
- Phím 'H': Bật/Tắt Mũ bảo hộ (Test kịch bản có/thiếu mũ)
- Phím 'V': Bật/Tắt Áo phản quang (Test kịch bản có/thiếu áo)
- Phím 'T': Bật/Tắt Cầm mũ trên tay (Test luật hình học phát hiện gian lận)
"""
import cv2
import argparse
import sys
import time
import numpy as np
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm đường dẫn gốc để chạy trực tiếp
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from safegate.config import DEFAULT_CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from safegate.core.pipeline import SafeGatePipeline, GateState
from safegate.core.geometric_rules import DetectionBox

class VirtualCamera:
    """Bộ giả lập nguồn phát Camera khi máy tính không có webcam vật lý"""
    def __init__(self, width=FRAME_WIDTH, height=FRAME_HEIGHT):
        self.w = width
        self.h = height
        self.frame_idx = 0
        self.has_helmet = True
        self.has_vest = True
        self.holding_helmet = False
        self.show_qr_card = False
        self._load_qr_image()

    def _load_qr_image(self):
        # Tạo ảnh QR test NV-1001 để render vào khung hình
        import qrcode
        qr = qrcode.QRCode(box_size=5, border=1)
        qr.add_data("SAFEGATE:NV-1001")
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        self.qr_np = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    def read(self):
        self.frame_idx += 1
        frame = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        # Nền xám xanh công nghiệp
        for y in range(self.h):
            ratio = y / self.h
            b = int(25 + 15 * ratio)
            g = int(30 + 15 * ratio)
            r = int(38 + 15 * ratio)
            frame[y, :] = (b, g, r)

        # Lưới công nghệ (Tech Grid)
        for x in range(0, self.w, 80):
            cv2.line(frame, (x, 0), (x, self.h), (45, 52, 65), 1)
        for y in range(0, self.h, 80):
            cv2.line(frame, (0, y), (self.w, y), (45, 52, 65), 1)

        # Cổng và sàn
        cv2.rectangle(frame, (0, self.h - 80), (self.w, self.h), (20, 24, 30), -1)
        cv2.line(frame, (0, self.h - 80), (self.w, self.h - 80), (14, 165, 233), 2)
        for x in range(0, self.w, 60):
            pts = np.array([[x, self.h - 25], [x + 30, self.h - 25], [x + 10, self.h], [x - 20, self.h]], np.int32)
            cv2.fillPoly(frame, [pts], (0, 180, 220))

        # Hiệu ứng chuyển động thở nhẹ của công nhân
        bob = int(np.sin(self.frame_idx * 0.1) * 3)

        # Thân người
        cv2.ellipse(frame, (640, 430 + bob), (130, 200), 0, 0, 360, (70, 80, 95), -1)
        # Đầu người
        cv2.circle(frame, (640, 230 + bob), 55, (190, 170, 160), -1)

        # Mũ bảo hộ
        if self.has_helmet:
            if self.holding_helmet:
                # Cầm ở tay
                cv2.ellipse(frame, (790, 480 + bob), (50, 35), 0, 0, 360, (0, 215, 255), -1)
            else:
                # Đội trên đầu
                cv2.ellipse(frame, (640, 190 + bob), (65, 40), 0, 180, 360, (0, 215, 255), -1)
                cv2.rectangle(frame, (570, 190 + bob), (710, 200 + bob), (0, 215, 255), -1)

        # Áo phản quang
        if self.has_vest:
            vx1, vy1, vx2, vy2 = 525, 280 + bob, 755, 530 + bob
            cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), (0, 230, 115), -1)
            cv2.line(frame, (vx1, 360 + bob), (vx2, 360 + bob), (240, 240, 240), 10)
            cv2.line(frame, (vx1, 440 + bob), (vx2, 440 + bob), (240, 240, 240), 10)

        # Nếu đang ở chế độ giơ thẻ QR
        if self.show_qr_card and self.qr_np is not None:
            qh, qw = self.qr_np.shape[:2]
            cx, cy = self.w // 2, self.h // 2
            # Vẽ nền thẻ trắng
            card_w, card_h = qw + 40, qh + 60
            cv2.rectangle(frame, (cx - card_w//2, cy - card_h//2), (cx + card_w//2, cy + card_h//2), (255, 255, 255), -1)
            cv2.rectangle(frame, (cx - card_w//2, cy - card_h//2), (cx + card_w//2, cy + card_h//2), (200, 200, 200), 2)
            # Dán mã QR vào tâm
            frame[cy - qh//2 : cy - qh//2 + qh, cx - qw//2 : cx - qw//2 + qw] = self.qr_np
            cv2.putText(frame, "NV-1001", (cx - 40, cy + qh//2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Watermark chế độ giả lập
        cv2.putText(frame, "[VIRTUAL CAMERA SIMULATOR]", (self.w - 320, self.h - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (14, 165, 233), 2, cv2.LINE_AA)

        return True, frame

    def release(self):
        pass

def main():
    parser = argparse.ArgumentParser(description="SafeGate Realtime PPE Gate-Check")
    parser.add_argument("--camera", type=int, default=DEFAULT_CAMERA_INDEX, help="Camera index (mặc định 0)")
    parser.add_argument("--video", type=str, default=None, help="Đường dẫn file video test (thay thế webcam)")
    parser.add_argument("--mock", action="store_true", help="Bắt buộc sử dụng Camera giả lập để test giao diện")
    args = parser.parse_args()

    print("=" * 60)
    print("   SAFEGATE - CỔNG KIỂM TRA ĐỒ BẢO HỘ LAO ĐỘNG (PPE) BẰNG AI")
    print("=" * 60)
    print("Đang khởi tạo hệ thống...")

    # Khởi tạo Pipeline
    pipeline = SafeGatePipeline()

    is_virtual = False
    cap = None

    if args.mock:
        print("[SafeGate] Đang sử dụng chế độ Giả lập Camera (Virtual Camera Simulator)...")
        cap = VirtualCamera()
        is_virtual = True
    else:
        source = args.video if args.video else args.camera
        real_cap = cv2.VideoCapture(source)
        if not real_cap.isOpened():
            print(f"[SafeGate Thông báo] Không tìm thấy camera vật lý hoặc file video ({source}).")
            print(">>> TỰ ĐỘNG CHUYỂN SANG CHẾ ĐỘ GIẢ LẬP CAMERA (VIRTUAL SIMULATOR) ĐỂ BẠN COI GIAO DIỆN! <<<")
            cap = VirtualCamera()
            is_virtual = True
        else:
            cap = real_cap
            if not args.video:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    window_name = "SafeGate - AI PPE Inspection System"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1100, 680)

    print("\n[HỆ THỐNG ĐÃ SẴN SÀNG]")
    print("- Nhấn phím 'S' để đưa thẻ nhân viên QR vào khung ngắm")
    print("- Hoặc nhấn [SPACE] để kích hoạt kiểm tra ngay")
    print("- Nhấn phím 'H' để bật/tắt Mũ bảo hộ")
    print("- Nhấn phím 'V' để bật/tắt Áo phản quang")
    print("- Nhấn phím 'T' để mô phỏng Cầm mũ trên tay (Gian lận)")
    print("- Nhấn 'Q' để thoát\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Nếu là camera ảo, đồng bộ cờ mô phỏng
            if is_virtual:
                pipeline.detector.simulation_helmet = cap.has_helmet
                pipeline.detector.simulation_vest = cap.has_vest

            # Xử lý frame qua Pipeline
            processed_frame = pipeline.process_frame(frame)

            # Cầm mũ trên tay giả lập
            if is_virtual and cap.holding_helmet and pipeline.state == GateState.CHECKING_PPE:
                # Đổi trạng thái hiển thị
                pass

            # Vẽ thanh hướng dẫn phím tắt ở đáy khung hình
            h, w = processed_frame.shape[:2]
            footer_text = "[S]: Dua the QR  |  [SPACE]: Check ngay  |  [H]: Mu  |  [V]: Ao  |  [T]: Cam tay  |  [R]: Reset  |  [Q]: Thoat"
            cv2.putText(processed_frame, footer_text, (20, h - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

            # Hiển thị cửa sổ
            cv2.imshow(window_name, processed_frame)

            # Xử lý phím bấm điều khiển
            key = cv2.waitKey(30 if is_virtual else 1) & 0xFF
            if key in (ord('q'), ord('Q'), 27):  # ESC or Q
                break
            elif key in (ord('s'), ord('S')):  # Giơ thẻ QR
                if is_virtual:
                    cap.show_qr_card = not cap.show_qr_card
                    st = "ĐANG GIƠ THẺ QR" if cap.show_qr_card else "ĐÃ CẤT THẺ"
                    print(f"[Simulate Card] {st}")
            elif key == ord(' '):  # SPACE
                print("[Action] Kích hoạt kiểm tra thủ công nhanh!")
                pipeline.trigger_manual_check("NV-1001")
            elif key in (ord('r'), ord('R')):
                print("[Action] Đặt lại hệ thống về trạng thái Chờ quét thẻ.")
                pipeline.reset_to_scan_state()
                if is_virtual:
                    cap.show_qr_card = False
            elif key in (ord('h'), ord('H')):
                if is_virtual:
                    cap.has_helmet = not cap.has_helmet
                    st = "BẬT" if cap.has_helmet else "TẮT (Thiếu mũ)"
                else:
                    pipeline.detector.simulation_helmet = not pipeline.detector.simulation_helmet
                    st = "BẬT" if pipeline.detector.simulation_helmet else "TẮT (Thiếu mũ)"
                print(f"[Test Toggle] Mũ bảo hộ: {st}")
            elif key in (ord('v'), ord('V')):
                if is_virtual:
                    cap.has_vest = not cap.has_vest
                    st = "BẬT" if cap.has_vest else "TẮT (Thiếu áo)"
                else:
                    pipeline.detector.simulation_vest = not pipeline.detector.simulation_vest
                    st = "BẬT" if pipeline.detector.simulation_vest else "TẮT (Thiếu áo)"
                print(f"[Test Toggle] Áo phản quang: {st}")
            elif key in (ord('t'), ord('T')):
                if is_virtual:
                    cap.holding_helmet = not cap.holding_helmet
                    st = "CẦM TAY (Gian lận)" if cap.holding_helmet else "ĐỘI TRÊN ĐẦU"
                print(f"[Test Toggle] Vị trí mũ: {st}")

    except KeyboardInterrupt:
        print("\n[SafeGate] Đang dừng chương trình...")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[SafeGate] Đã đóng cửa sổ thành công.")

if __name__ == "__main__":
    main()
