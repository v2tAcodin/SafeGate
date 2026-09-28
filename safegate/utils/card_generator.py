"""
Employee Card and QR Code Generator for SafeGate
Tạo thẻ nhân viên kèm mã QR chuẩn để in hoặc hiển thị trên màn hình điện thoại phục vụ test.
"""
from pathlib import Path
from typing import Optional
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_qr_image(data: str, box_size: int = 10, border: int = 2) -> Image.Image:
    """Tạo ảnh QR Code cơ bản"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def generate_employee_badge(employee_code: str, full_name: str, department: str,
                            save_path: Optional[Path] = None) -> Image.Image:
    """
    Tạo thẻ nhân viên đồ họa chuyên nghiệp (Badge Card):
    - Logo / Banner SafeGate
    - Tên, phòng ban, mã số
    - Mã QR kích thước chuẩn
    """
    card_w, card_h = 500, 700
    badge = Image.new("RGB", (card_w, card_h), color=(245, 247, 250))
    draw = ImageDraw.Draw(badge)

    # Header Banner màu xanh than
    draw.rectangle([(0, 0), (card_w, 120)], fill=(30, 41, 59))
    draw.rectangle([(0, 115), (card_w, 120)], fill=(14, 165, 233))  # Viền nhấn xanh cyan

    # Chữ Header
    draw.text((card_w // 2, 45), "SAFEGATE", fill=(255, 255, 255), anchor="mm")
    draw.text((card_w // 2, 85), "THE NHAN VIEN CONG TRUONG", fill=(148, 163, 184), anchor="mm")

    # Tạo mã QR cho nhân viên
    qr_img = generate_qr_image(f"SAFEGATE:{employee_code}", box_size=7, border=2)
    qr_w, qr_h = qr_img.size
    qr_x = (card_w - qr_w) // 2
    qr_y = 150
    badge.paste(qr_img, (qr_x, qr_y))

    # Viền quanh QR
    draw.rectangle([(qr_x - 5, qr_y - 5), (qr_x + qr_w + 5, qr_y + qr_h + 5)], outline=(203, 213, 225), width=2)

    # Thông tin nhân viên
    info_y = qr_y + qr_h + 35
    draw.text((card_w // 2, info_y), full_name.upper(), fill=(15, 23, 42), anchor="mm")
    draw.text((card_w // 2, info_y + 35), f"Ma NV: {employee_code}", fill=(2, 132, 199), anchor="mm")
    draw.text((card_w // 2, info_y + 70), f"Bo phan: {department}", fill=(71, 85, 105), anchor="mm")

    # Footer
    draw.rectangle([(0, card_h - 40), (card_w, card_h)], fill=(226, 232, 240))
    draw.text((card_w // 2, card_h - 20), "Vui long xuat trinh tai cong SafeGate truoc khi vao", fill=(100, 116, 139), anchor="mm")

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        badge.save(str(save_path))

    return badge
