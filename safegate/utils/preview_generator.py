"""
SafeGate UI Preview Generator
Tạo các ảnh chụp màn hình giao diện (Screenshots) chuẩn xác của hệ thống:
1. Giao diện Chờ quét thẻ (SCANNING_QR)
2. Giao diện Đang kiểm tra PPE với Voting 8/10 (CHECKING_PPE)
3. Giao diện ĐẠT (PASS - Xanh lá)
4. Giao diện KHÔNG ĐẠT (FAIL - Đỏ) do thiếu mũ bảo hộ
5. Giao diện KHÔNG ĐẠT (FAIL - Đỏ) do cầm mũ trên tay (Gian lận)
"""
import cv2
import numpy as np
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from safegate.utils.visualizer import GateVisualizer
from safegate.core.geometric_rules import DetectionBox, EvaluationResult

def create_simulated_scene(w=1280, h=720, state="idle", has_helmet=True, has_vest=True, holding_helmet=False):
    """Vẽ phối cảnh công nhân tại cổng kiểm soát SafeGate"""
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Nền xám xanh công nghiệp
    for y in range(h):
        ratio = y / h
        b = int(25 + 15 * ratio)
        g = int(30 + 15 * ratio)
        r = int(38 + 15 * ratio)
        frame[y, :] = (b, g, r)

    # Lưới grid công nghệ
    for x in range(0, w, 80):
        cv2.line(frame, (x, 0), (x, h), (45, 52, 65), 1)
    for y in range(0, h, 80):
        cv2.line(frame, (y, 0), (w, y), (45, 52, 65), 1)

    # Vẽ sàn và cổng
    cv2.rectangle(frame, (0, h - 80), (w, h), (20, 24, 30), -1)
    cv2.line(frame, (0, h - 80), (w, h - 80), (14, 165, 233), 2)

    # Vẽ vạch kẻ an toàn màu vàng/đen ở chân
    for x in range(0, w, 60):
        pts = np.array([[x, h - 25], [x + 30, h - 25], [x + 10, h], [x - 20, h]], np.int32)
        cv2.fillPoly(frame, [pts], (0, 180, 220))

    # Tọa độ người
    px1, py1, px2, py2 = 490, 160, 790, 640
    pw = px2 - px1
    ph = py2 - py1

    # Thân người (Silhoutte áo xanh đậm hoặc bảo hộ)
    cv2.ellipse(frame, (640, 430), (130, 200), 0, 0, 360, (70, 80, 95), -1)
    # Đầu người
    cv2.circle(frame, (640, 230), 55, (190, 170, 160), -1)

    # Danh sách detection giả lập
    detections = [
        DetectionBox(class_name="person", confidence=0.94, x1=px1, y1=py1, x2=px2, y2=py2)
    ]

    # Mũ bảo hộ
    if has_helmet:
        if holding_helmet:
            # Cầm ở tay
            hx1, hy1, hx2, hy2 = 740, 440, 840, 520
            # Vẽ mũ cầm tay
            cv2.ellipse(frame, (790, 480), (50, 35), 0, 0, 360, (0, 215, 255), -1)
            detections.append(DetectionBox(class_name="helmet", confidence=0.89, x1=hx1, y1=hy1, x2=hx2, y2=hy2))
        else:
            # Đội trên đầu chuẩn
            hx1, hy1, hx2, hy2 = 575, 150, 705, 225
            cv2.ellipse(frame, (640, 190), (65, 40), 0, 180, 360, (0, 215, 255), -1)
            cv2.rectangle(frame, (570, 190), (710, 200), (0, 215, 255), -1)
            detections.append(DetectionBox(class_name="helmet", confidence=0.92, x1=hx1, y1=hy1, x2=hx2, y2=hy2))

    # Áo phản quang
    if has_vest:
        vx1, vy1, vx2, vy2 = 525, 280, 755, 530
        cv2.rectangle(frame, (vx1, vy1), (vx2, vy2), (0, 230, 115), -1)
        # Vạch bạc phản quang
        cv2.line(frame, (vx1, 360), (vx2, 360), (240, 240, 240), 10)
        cv2.line(frame, (vx1, 440), (vx2, 440), (240, 240, 240), 10)
        detections.append(DetectionBox(class_name="vest", confidence=0.88, x1=vx1, y1=vy1, x2=vx2, y2=vy2))

    return frame, detections

def generate_previews():
    vis = GateVisualizer()
    out_dir = BASE_DIR / "previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    emp_sample = {
        "employee_code": "NV-1001",
        "full_name": "Nguyen Van An",
        "department": "Thi cong ket cau",
        "role": "Tho sat"
    }

    # =========================================================================
    # PREVIEW 1: TRẠNG THÁI QUÉT THẺ (SCANNING_QR)
    # =========================================================================
    f1, _ = create_simulated_scene(state="qr")
    # Vẽ thẻ mẫu trong khung quét
    cx, cy = 640, 360
    card_w, card_h = 240, 160
    cv2.rectangle(f1, (cx - card_w//2, cy - card_h//2), (cx + card_w//2, cy + card_h//2), (240, 240, 240), -1)
    cv2.rectangle(f1, (cx - 70, cy - 70), (cx + 70, cy + 70), (30, 30, 30), 2)
    # 4 góc QR
    pts = np.array([[cx - 65, cy - 65], [cx + 65, cy - 65], [cx + 65, cy + 65], [cx - 65, cy + 65]])
    vis.draw_qr_scan_zone(f1, pts)
    vis.draw_hud_header(f1, "CHO QUET THE", None, 30.0, "0/10", 0.0)
    cv2.imwrite(str(out_dir / "01_scanning_qr.png"), f1)

    # =========================================================================
    # PREVIEW 2: ĐANG KIỂM TRA PPE (CHECKING_PPE)
    # =========================================================================
    f2, d2 = create_simulated_scene(has_helmet=True, has_vest=True)
    eval2 = EvaluationResult(has_person=True, helmet_on_head=True, vest_on_torso=True, is_compliant=True)
    vis.draw_detections(f2, d2, eval2)
    vis.draw_hud_header(f2, "DANG KIEM TRA PPE", emp_sample, 28.5, "6/10", 0.75)
    cv2.imwrite(str(out_dir / "02_checking_ppe.png"), f2)

    # =========================================================================
    # PREVIEW 3: KẾT QUẢ ĐẠT (PASS - XANH LÁ)
    # =========================================================================
    f3, d3 = create_simulated_scene(has_helmet=True, has_vest=True)
    eval3 = EvaluationResult(has_person=True, helmet_on_head=True, vest_on_torso=True, is_compliant=True)
    vis.draw_detections(f3, d3, eval3)
    vis.draw_hud_header(f3, "KET QUA: PASS", emp_sample, 30.0, "10/10", 1.0)
    vis.draw_result_banner(f3, "PASS", [])
    cv2.imwrite(str(out_dir / "03_result_pass.png"), f3)

    # =========================================================================
    # PREVIEW 4: KẾT QUẢ FAIL DO THIẾU MŨ BẢO HỘ
    # =========================================================================
    f4, d4 = create_simulated_scene(has_helmet=False, has_vest=True)
    eval4 = EvaluationResult(has_person=True, helmet_on_head=False, vest_on_torso=True, is_compliant=False, missing_items=["Mu bao ho"])
    vis.draw_detections(f4, d4, eval4)
    vis.draw_hud_header(f4, "KET QUA: FAIL", emp_sample, 29.2, "2/10", 0.2)
    vis.draw_result_banner(f4, "FAIL", ["Mu bao ho"])
    cv2.imwrite(str(out_dir / "04_result_fail_missing_helmet.png"), f4)

    # =========================================================================
    # PREVIEW 5: KẾT QUẢ FAIL DO CẦM MŨ TRÊN TAY (LUẬT HÌNH HỌC)
    # =========================================================================
    f5, d5 = create_simulated_scene(has_helmet=True, has_vest=True, holding_helmet=True)
    eval5 = EvaluationResult(has_person=True, helmet_on_head=False, vest_on_torso=True, is_holding_helmet=True, is_compliant=False, missing_items=["Mu bao ho (Dang cam tay, chua doi)"])
    eval5.matched_helmet = d5[1]
    vis.draw_detections(f5, d5, eval5)
    vis.draw_hud_header(f5, "KET QUA: FAIL", emp_sample, 29.5, "3/10", 0.3)
    vis.draw_result_banner(f5, "FAIL", ["Mu bao ho (Dang cam tay, chua doi)"])
    cv2.imwrite(str(out_dir / "05_result_fail_holding_helmet.png"), f5)

    print(f"5 ảnh giao diện chất lượng cao đã được tạo tại: {out_dir}")

if __name__ == "__main__":
    generate_previews()
