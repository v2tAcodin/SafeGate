"""
SafeGate FastAPI Server
Cung cấp REST API & MJPEG Video Streaming cho ứng dụng Flutter Frontend:
- GET /video_feed: Luồng video trực tiếp 30 FPS kèm HUD & Bounding Box cho Flutter
- GET /api/stats: Số liệu thống kê tổng quan
- GET /api/logs: Lịch sử kiểm tra ra vào cổng
- GET /api/employees & POST /api/employees: Quản lý danh sách nhân viên
- GET /api/badge/{code}: Tải ảnh thẻ nhân viên kèm mã QR
- POST /api/control: Điều khiển giả lập (Bật/tắt mũ, áo, cầm tay, kích hoạt check)
"""
import io
import time
import cv2
import numpy as np
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from safegate.database.db_manager import DatabaseManager
from safegate.core.pipeline import SafeGatePipeline, GateState
from safegate.run_gate import VirtualCamera
from safegate.utils.card_generator import generate_employee_badge
from safegate.config import DEFAULT_CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

app = FastAPI(title="SafeGate AI PPE API", version="1.0.0")

# Cấu hình CORS để Flutter Web & Desktop gọi API mượt mà
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo DB & Pipeline
db = DatabaseManager()
pipeline = SafeGatePipeline(db_manager=db)

# Khởi tạo nguồn Camera (Webcam vật lý hoặc Virtual Camera nếu không có webcam)
real_cap = cv2.VideoCapture(DEFAULT_CAMERA_INDEX)
if not real_cap.isOpened():
    print("[SafeGate API] Không tìm thấy webcam vật lý -> Sử dụng Virtual Camera cho Flutter Stream!")
    active_camera = VirtualCamera()
    is_virtual_cam = True
else:
    active_camera = real_cap
    active_camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    active_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    is_virtual_cam = False

class EmployeeCreateRequest(BaseModel):
    employee_code: str
    full_name: str
    department: str
    role: str = "Công nhân"

class ControlActionRequest(BaseModel):
    action: str  # 'check', 'reset', 'scan_card', 'toggle_helmet', 'toggle_vest', 'toggle_holding'
    employee_code: Optional[str] = "NV-1001"

@app.get("/")
def read_root():
    return {"status": "online", "system": "SafeGate AI PPE Gate-Check", "version": "1.0.0"}

@app.get("/api/state")
def get_state():
    """Lấy trạng thái hiện tại của Cổng kiểm tra"""
    return {
        "state": pipeline.state.value,
        "employee": pipeline.current_employee,
        "fps": round(pipeline.fps, 1),
        "voting_score": pipeline.voter.current_score_str,
        "final_status": pipeline.final_status,
        "missing_items": pipeline.final_missing_items,
        "is_virtual_cam": is_virtual_cam,
        "sim_helmet": pipeline.detector.simulation_helmet,
        "sim_vest": pipeline.detector.simulation_vest
    }

def frame_generator():
    """Bộ sinh luồng MJPEG Video Stream thời gian thực"""
    global active_camera, is_virtual_cam, pipeline
    while True:
        ret, frame = active_camera.read()
        if not ret or frame is None:
            time.sleep(0.03)
            continue

        # Đồng bộ cờ mô phỏng nếu là Virtual Camera
        if is_virtual_cam:
            pipeline.detector.simulation_helmet = active_camera.has_helmet
            pipeline.detector.simulation_vest = active_camera.has_vest

        # Xử lý frame qua pipeline SafeGate (HUD, bounding box, QR, voting)
        processed = pipeline.process_frame(frame)

        # Encode sang định dạng JPEG chất lượng cao
        ret, buffer = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        time.sleep(0.033)  # ~30 FPS

@app.get("/video_feed")
def video_feed():
    """Endpoint Stream Video MJPEG dùng cho Widget Image.network trong Flutter"""
    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/api/stats")
def get_stats():
    """Thống kê tổng quan phục vụ Dashboard Flutter"""
    return db.get_statistics()

@app.get("/api/logs")
def get_logs(limit: int = 100, status: Optional[str] = None, search: Optional[str] = None):
    """Lấy lịch sử nhật ký kiểm tra ra vào cổng"""
    return db.get_logs(limit=limit, status_filter=status, search_keyword=search)

@app.get("/api/employees")
def list_employees():
    """Danh sách nhân viên trong cơ sở dữ liệu"""
    return db.list_employees()

@app.post("/api/employees")
def add_employee(emp: EmployeeCreateRequest):
    """Đăng ký nhân viên mới"""
    success = db.add_employee(emp.employee_code, emp.full_name, emp.department, emp.role)
    if not success:
        raise HTTPException(status_code=400, detail="Mã nhân viên đã tồn tại")
    return {"message": "Thêm nhân viên thành công", "employee_code": emp.employee_code}

@app.get("/api/badge/{code}")
def get_employee_badge_image(code: str):
    """Sinh và trả về ảnh thẻ nhân viên có gắn mã QR trực tiếp"""
    emp = db.get_employee_by_code(code)
    if not emp:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")

    badge = generate_employee_badge(
        employee_code=emp["employee_code"],
        full_name=emp["full_name"],
        department=emp["department"]
    )
    buf = io.BytesIO()
    badge.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.post("/api/control")
def control_gate(req: ControlActionRequest):
    """Các lệnh điều khiển nhanh từ nút bấm trên giao diện Flutter"""
    global active_camera, is_virtual_cam, pipeline
    action = req.action.lower()

    if action == "check":
        pipeline.trigger_manual_check(req.employee_code or "NV-1001")
        return {"status": "ok", "action": "triggered_check"}

    elif action == "reset":
        pipeline.reset_to_scan_state()
        if is_virtual_cam:
            active_camera.show_qr_card = False
        return {"status": "ok", "action": "reset"}

    elif action == "scan_card":
        if is_virtual_cam:
            active_camera.show_qr_card = not active_camera.show_qr_card
            return {"status": "ok", "showing_card": active_camera.show_qr_card}
        else:
            pipeline.trigger_manual_check(req.employee_code or "NV-1001")
            return {"status": "ok", "action": "manual_scan"}

    elif action == "toggle_helmet":
        if is_virtual_cam:
            active_camera.has_helmet = not active_camera.has_helmet
            cur = active_camera.has_helmet
        else:
            pipeline.detector.simulation_helmet = not pipeline.detector.simulation_helmet
            cur = pipeline.detector.simulation_helmet
        return {"status": "ok", "helmet": cur}

    elif action == "toggle_vest":
        if is_virtual_cam:
            active_camera.has_vest = not active_camera.has_vest
            cur = active_camera.has_vest
        else:
            pipeline.detector.simulation_vest = not pipeline.detector.simulation_vest
            cur = pipeline.detector.simulation_vest
        return {"status": "ok", "vest": cur}

    elif action == "toggle_holding":
        if is_virtual_cam:
            active_camera.holding_helmet = not active_camera.holding_helmet
            cur = active_camera.holding_helmet
            return {"status": "ok", "holding_helmet": cur}

    return {"status": "unknown_action"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("safegate.api.server:app", host="0.0.0.0", port=8000, reload=False)
