"""
SafeGate - Streamlit Web Dashboard & Management Portal
Cổng quản lý và phân tích hệ thống kiểm tra đồ bảo hộ SafeGate:
- Dashboard thống kê tỷ lệ PASS/FAIL, vi phạm phổ biến.
- Báo cáo chi tiết lịch sử và chức năng Xuất file CSV.
- Quản lý nhân viên & Sinh thẻ nhân viên kèm mã QR để test.
- Công cụ kiểm tra ảnh/webcam trực tiếp trên giao diện web.
- Tối ưu hiệu năng: Export ONNX, Quantize INT8 và Benchmark FPS/Latency.
"""
import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from pathlib import Path
import sys

# Đảm bảo đường dẫn import đúng module safegate
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from safegate.database.db_manager import DatabaseManager
from safegate.core.geometric_rules import GeometricRuleValidator, DetectionBox
from safegate.core.detector import PPEDetector
from safegate.core.onnx_exporter import ModelOptimizer
from safegate.utils.card_generator import generate_employee_badge, generate_qr_image
from safegate.utils.visualizer import GateVisualizer

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="SafeGate - AI PPE Inspection",
    page_icon="🦺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Slate & Neon Green/Amber Theme)
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0ea5e9;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 24px;
    }
    .stat-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 24px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .stat-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .stat-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .pass-tag {
        background-color: rgba(34, 197, 94, 0.2);
        color: #4ade80;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    .fail-tag {
        background-color: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.85rem;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo kết nối DB dùng chung
@st.cache_resource
def get_db():
    return DatabaseManager()

@st.cache_resource
def get_detector():
    return PPEDetector()

db = get_db()

# Sidebar
st.sidebar.image("https://img.icons8.com/isometric/512/hard-hat.png", width=70)
st.sidebar.markdown("## **SafeGate Control**")
st.sidebar.markdown("*Hệ thống AI kiểm tra PPE & Cổng an toàn lao động*")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "CHỨC NĂNG HỆ THỐNG",
    [
        "📊 Thống kê & Báo cáo",
        "🎫 Thẻ nhân viên & Mã QR",
        "📷 Kiểm tra thử nghiệm (Simulator)",
        "⚡ Tối ưu hiệu năng (ONNX)",
        "📘 Tài liệu đề tài CNPM"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("""
**Nguyên tắc bảo vệ dữ liệu:**
Tuân thủ tiêu chuẩn quyền riêng tư công nhân: **Tuyệt đối không lưu ảnh** vào cơ sở dữ liệu.
""")

# ==============================================================================
# TAB 1: THỐNG KÊ & BÁO CÁO (DASHBOARD & REPORTS)
# ==============================================================================
if menu == "📊 Thống kê & Báo cáo":
    st.markdown('<p class="main-title">SAFEGATE ANALYTICS & REPORTS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Báo cáo kiểm soát tuân thủ trang bị bảo hộ lao động theo thời gian thực</p>', unsafe_allow_html=True)

    stats = db.get_statistics()

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Tổng lượt kiểm tra</div>
            <div class="stat-val">{stats['total_checks']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Lượt Đạt (PASS)</div>
            <div class="stat-val" style="color: #4ade80;">{stats['pass_count']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Lượt Vi phạm (FAIL)</div>
            <div class="stat-val" style="color: #f87171;">{stats['fail_count']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Tỷ lệ tuân thủ</div>
            <div class="stat-val" style="color: #38bdf8;">{stats['pass_rate']}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Biểu đồ và danh sách vi phạm
    g_col1, g_col2 = st.columns([1, 1])
    with g_col1:
        st.markdown("### 📈 Phân bố kết quả kiểm tra")
        if stats['total_checks'] > 0:
            df_pie = pd.DataFrame({
                "Kết quả": ["PASS (Đạt)", "FAIL (Vi phạm)"],
                "Số lượt": [stats['pass_count'], stats['fail_count']]
            })
            st.bar_chart(df_pie.set_index("Kết quả"))
        else:
            st.info("Chưa có lượt kiểm tra nào được ghi nhận.")

    with g_col2:
        st.markdown("### ⚠️ Các vi phạm an toàn phổ biến nhất")
        if stats['top_violations']:
            v_df = pd.DataFrame(stats['top_violations'])
            v_df.columns = ["Lỗi vi phạm", "Số lần ghi nhận"]
            st.dataframe(v_df, use_container_width=True, hide_index=True)
        else:
            st.success("Không có vi phạm an toàn nào được ghi nhận.")

    st.markdown("---")
    st.markdown("### 📋 Nhật ký ra vào cổng (Access History)")

    # Bộ lọc
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col1:
        status_filter = st.selectbox("Lọc theo trạng thái:", ["Tất cả", "PASS", "FAIL"])
    with f_col2:
        keyword = st.text_input("Tìm kiếm theo tên, mã NV, bộ phận:", "")
    with f_col3:
        limit = st.slider("Số lượng bản ghi tối đa:", 10, 500, 100)

    filter_val = None if status_filter == "Tất cả" else status_filter
    logs = db.get_logs(limit=limit, status_filter=filter_val, search_keyword=keyword)

    if logs:
        df_logs = pd.DataFrame(logs)
        display_cols = ["id", "timestamp", "employee_code", "employee_name", "department", "status", "missing_items", "vote_score", "check_duration"]
        col_names = ["ID", "Thời gian", "Mã NV", "Họ tên", "Bộ phận", "Trạng thái", "Món thiếu", "Điểm Voting", "Thời lượng (s)"]
        df_display = df_logs[display_cols]
        df_display.columns = col_names

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Nút xuất file CSV (theo đúng yêu cầu spec)
        csv_data = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Xuất báo cáo ra file CSV (Excel compatible)",
            data=csv_data,
            file_name="safegate_access_logs.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.warning("Không tìm thấy bản ghi nào phù hợp với bộ lọc.")

# ==============================================================================
# TAB 2: THẺ NHÂN VIÊN & MÃ QR (EMPLOYEES & BADGES)
# ==============================================================================
elif menu == "🎫 Thẻ nhân viên & Mã QR":
    st.markdown('<p class="main-title">QUẢN LÝ NHÂN VIÊN & TẠO THẺ QR</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Tạo và xuất thẻ nhân viên có gắn mã QR chuẩn để quét tại cổng kiểm tra</p>', unsafe_allow_html=True)

    employees = db.list_employees()

    col_list, col_card = st.columns([1.2, 1])

    with col_list:
        st.markdown("### 👥 Danh sách nhân viên trong cơ sở dữ liệu")
        if employees:
            emp_df = pd.DataFrame(employees)[["employee_code", "full_name", "department", "role"]]
            emp_df.columns = ["Mã NV", "Họ và tên", "Bộ phận", "Chức danh"]
            st.dataframe(emp_df, use_container_width=True, hide_index=True)

        st.markdown("#### ➕ Đăng ký thêm nhân viên mới")
        with st.form("add_employee_form"):
            new_code = st.text_input("Mã nhân viên (duy nhất):", placeholder="NV-1008")
            new_name = st.text_input("Họ và tên:", placeholder="Nguyễn Văn X")
            new_dept = st.text_input("Bộ phận / Nhà thầu:", placeholder="Cơ điện MEP")
            new_role = st.selectbox("Chức danh:", ["Công nhân", "Kỹ sư", "Cán bộ an toàn HSE", "Giám sát", "Khách"])
            submitted = st.form_submit_button("Thêm nhân viên", type="primary")

            if submitted:
                if new_code and new_name and new_dept:
                    if db.add_employee(new_code, new_name, new_dept, new_role):
                        st.success(f"Đã thêm thành công nhân viên {new_code} - {new_name}")
                        st.rerun()
                    else:
                        st.error(f"Mã nhân viên {new_code} đã tồn tại trong hệ thống!")
                else:
                    st.warning("Vui lòng nhập đầy đủ các trường thông tin.")

    with col_card:
        st.markdown("### 🪪 Thẻ nhân viên chuẩn (Preview & Download)")
        if employees:
            selected_code = st.selectbox("Chọn nhân viên để xem và in thẻ:", [e["employee_code"] for e in employees])
            emp_info = db.get_employee_by_code(selected_code)

            if emp_info:
                # Tạo thẻ đồ họa
                badge_img = generate_employee_badge(
                    employee_code=emp_info["employee_code"],
                    full_name=emp_info["full_name"],
                    department=emp_info["department"]
                )

                st.image(badge_img, caption=f"Thẻ định danh {emp_info['employee_code']}", use_container_width=True)

                # Nút tải thẻ
                buf = BytesIO()
                badge_img.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="💾 Tải thẻ nhân viên (PNG)",
                    data=byte_im,
                    file_name=f"Badge_{emp_info['employee_code']}.png",
                    mime="image/png"
                )
                st.caption("💡 Mẹo: Mở ảnh này trên điện thoại hoặc in ra giấy rồi đưa trước webcam để hệ thống quét tự động!")

# ==============================================================================
# TAB 3: KIỂM TRA THỬ NGHIỆM (SIMULATOR)
# ==============================================================================
elif menu == "📷 Kiểm tra thử nghiệm (Simulator)":
    st.markdown('<p class="main-title">CỔNG KIỂM TRA THỬ NGHIỆM</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Kiểm tra thuật toán AI và Luật hình học trực tiếp bằng ảnh tải lên hoặc webcam</p>', unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 1])

    with sim_col1:
        input_type = st.radio("Chọn nguồn ảnh:", ["Tải ảnh lên (Upload File)", "Chụp ảnh từ Camera"], horizontal=True)
        img_file = None

        if input_type == "Tải ảnh lên (Upload File)":
            img_file = st.file_uploader("Chọn ảnh kiểm tra (JPG/PNG):", type=["jpg", "jpeg", "png"])
        else:
            img_file = st.camera_input("Chụp ảnh kiểm tra từ webcam:")

        # Tùy chọn test kịch bản
        st.markdown("#### ⚙️ Thiết lập kịch bản thử nghiệm")
        sim_helmet = st.checkbox("Có mũ bảo hộ", value=True)
        sim_vest = st.checkbox("Có áo phản quang", value=True)
        sim_holding = st.checkbox("Mô phỏng gian lận: Cầm mũ trên tay", value=False)
        selected_emp_code = st.selectbox("Nhân viên thực hiện kiểm tra:", [e["employee_code"] for e in db.list_employees()])

    with sim_col2:
        st.markdown("### 🖥️ Kết quả phân tích từ AI & Luật hình học")
        if img_file is not None:
            # Đọc ảnh sang OpenCV format
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            frame = cv2.imdecode(file_bytes, 1)

            if frame is not None:
                h, w = frame.shape[:2]
                detector = get_detector()
                detector.simulation_helmet = sim_helmet
                detector.simulation_vest = sim_vest

                # Nhận diện
                detections = detector.detect(frame)

                # Nếu mô phỏng cầm mũ trên tay
                if sim_holding:
                    for d in detections:
                        if d.class_name == "helmet":
                            # Dời tâm mũ xuống vị trí tay (60% chiều cao người)
                            people = [p for p in detections if p.class_name == "person"]
                            if people:
                                p = people[0]
                                d.y1 = p.y1 + p.height * 0.55
                                d.y2 = d.y1 + p.height * 0.2

                # Đánh giá bằng luật hình học
                validator = GeometricRuleValidator()
                eval_res = validator.evaluate_frame(detections, w, h)

                # Vẽ giao diện trực quan
                vis = GateVisualizer()
                annotated = frame.copy()
                vis.draw_detections(annotated, detections, eval_res)

                # Vẽ kết quả banner
                status = "PASS" if eval_res.is_compliant else "FAIL"
                vis.draw_result_banner(annotated, status, eval_res.missing_items)

                # Chuyển BGR sang RGB để hiển thị trên Streamlit
                annotated_rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, use_container_width=True)

                # Hiển thị thông báo chi tiết
                if eval_res.is_compliant:
                    st.success("✅ **KẾT QUẢ: PASS (ĐẠT)** - Đầy đủ mũ bảo hộ và áo phản quang đúng vị trí quy chuẩn.")
                else:
                    st.error(f"❌ **KẾT QUẢ: FAIL (KHÔNG ĐẠT)** - {eval_res.detail_message}")

                # Nút ghi nhận vào log
                if st.button("📝 Lưu kết quả này vào Database", type="primary"):
                    emp = db.get_employee_by_code(selected_emp_code)
                    db.log_access(
                        employee_code=emp["employee_code"],
                        employee_name=emp["full_name"],
                        department=emp["department"],
                        status=status,
                        missing_items=eval_res.missing_items,
                        vote_score="10/10" if eval_res.is_compliant else "3/10",
                        duration=1.2
                    )
                    st.toast("Đã ghi log thành công vào SQLite (Không lưu ảnh)! 🎉")
        else:
            st.info("Vui lòng tải lên ảnh hoặc chụp từ webcam để xem kết quả phân tích thời gian thực.")

# ==============================================================================
# TAB 4: TỐI ƯU HIỆU NĂNG (ONNX & BENCHMARK)
# ==============================================================================
elif menu == "⚡ Tối ưu hiệu năng (ONNX)":
    st.markdown('<p class="main-title">TỐI ƯU HIỆU NĂNG & BENCHMARK</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Tối ưu hóa mô hình YOLO nano: Export ONNX, Lượng tử hóa INT8 và kiểm thử FPS/Latency trên laptop</p>', unsafe_allow_html=True)

    optimizer = ModelOptimizer()

    b_col1, b_col2 = st.columns([1, 1])

    with b_col1:
        st.markdown("### ⚙️ Thao tác tối ưu hóa mô hình")
        model_choice = st.selectbox("Chọn mô hình gốc:", ["yolov8n.pt (YOLOv8 Nano)", "safegate_best.pt (Custom)"])
        model_file = "yolov8n.pt" if "yolov8n" in model_choice else "safegate/models/safegate_best.pt"

        if st.button("🚀 1. Export sang định dạng ONNX", use_container_width=True):
            with st.spinner("Đang xuất mô hình sang ONNX..."):
                out_path = optimizer.export_onnx(model_file)
                if out_path:
                    st.success(f"Xuất ONNX thành công: `{out_path}`")
                else:
                    st.error("Lỗi khi xuất ONNX.")

        onnx_candidate = Path("yolov8n.onnx")
        if onnx_candidate.exists():
            if st.button("📦 2. Lượng tử hóa INT8 (Quantization)", use_container_width=True):
                with st.spinner("Đang thực hiện lượng tử hóa sang INT8..."):
                    int8_path = optimizer.quantize_int8(str(onnx_candidate))
                    if int8_path:
                        st.success(f"Lượng tử hóa INT8 thành công: `{int8_path}`")

    with b_col2:
        st.markdown("### ⏱️ Đo lường hiệu năng thực tế (Benchmark)")
        bench_runs = st.slider("Số vòng kiểm thử (Iterations):", 10, 50, 20)

        if st.button("📊 Chạy Benchmark trên CPU Laptop", type="primary", use_container_width=True):
            with st.spinner("Đang chạy kiểm thử hiệu năng..."):
                bench_res = optimizer.benchmark(model_target=model_file, num_runs=bench_runs)
                
                st.markdown(f"""
                <div class="stat-card" style="margin-top: 15px;">
                    <div class="stat-label">Tốc độ ước tính (FPS)</div>
                    <div class="stat-val" style="color: #4ade80;">{bench_res['estimated_fps']} FPS</div>
                </div>
                """, unsafe_allow_html=True)

                m1, m2 = st.columns(2)
                with m1:
                    st.metric("Độ trễ trung bình (Latency)", f"{bench_res['avg_latency_ms']} ms")
                with m2:
                    st.metric("Dung lượng mô hình", f"{bench_res['file_size_mb']} MB")

# ==============================================================================
# TAB 5: TÀI LIỆU ĐỀ TÀI CNPM
# ==============================================================================
elif menu == "📘 Tài liệu đề tài CNPM":
    st.markdown('<p class="main-title">TÀI LIỆU DỰ ÁN SAFEGATE</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Đề tài môn Công nghệ phần mềm (CNPM) - Kế hoạch 5 tuần</p>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 Mục tiêu dự án
    Hệ thống cổng kiểm soát an toàn lao động tại lối vào công trường:
    - Công nhân đứng trước webcam, đưa thẻ QR để định danh.
    - Hệ thống AI tự động kiểm tra mũ bảo hộ và áo phản quang theo luật hình học (mũ trên đầu, áo trên thân).
    - Bộ lọc voting 8/10 khung hình loại bỏ nhiễu nhấp nháy.
    - Trả kết quả PASS (Xanh) hoặc FAIL (Đỏ) và lưu log SQLite (Không lưu ảnh bảo vệ quyền riêng tư).

    ---

    ### 🗓️ Kế hoạch thực hiện 5 tuần (50 giờ)
    - **Tuần 1: Khởi động & Chuẩn bị dữ liệu**
      - Thu thập dataset PPE (Roboflow Universe/SHWD/CHV).
      - Thiết lập cấu trúc dự án và cơ sở dữ liệu SQLite.
    - **Tuần 2: Xây dựng AI Detector & Training**
      - Huấn luyện YOLO nano (person, helmet, vest) trên Colab/Kaggle.
      - Xây dựng module nhận diện cơ bản.
    - **Tuần 3: Thuật toán cốt lõi (Core Engine)**
      - Phát triển luật hình học (Geometric Rule) chống cầm mũ trên tay.
      - Phát triển bộ lọc Voting đa khung hình 8/10.
      - Tích hợp module quét mã QR thẻ nhân viên.
    - **Tuần 4: Giao diện trực quan & Quản trị**
      - Giao diện OpenCV Realtime Gate Runner với HUD và Banner kết quả.
      - Dashboard Streamlit: Báo cáo, Thống kê, Xuất CSV, Quản lý thẻ QR.
    - **Tuần 5: Tối ưu hóa & Kiểm thử nghiệm thu**
      - Export ONNX, Quantize INT8, Benchmark FPS/Latency trên laptop.
      - Kiểm thử độc lập trên tập test riêng biệt và hoàn thiện báo cáo môn CNPM.
    """)
