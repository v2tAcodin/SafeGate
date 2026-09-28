"""
SafeGate - Main Launcher
Bộ khởi chạy trung tâm cho hệ thống SafeGate
"""
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_DIR = Path(__file__).resolve().parent
PYTHON_EXE = PROJECT_DIR / ".venv" / "Scripts" / "python.exe"

def run_gate():
    print("\n[SafeGate] Đang khởi chạy Cổng kiểm tra thời gian thực với Webcam (OpenCV)...")
    subprocess.run([str(PYTHON_EXE), str(PROJECT_DIR / "safegate" / "run_gate.py")])

def run_dashboard():
    print("\n[SafeGate] Đang khởi chạy Cổng quản trị Web Dashboard (Streamlit)...")
    streamlit_exe = PROJECT_DIR / ".venv" / "Scripts" / "streamlit.exe"
    subprocess.run([str(streamlit_exe), "run", str(PROJECT_DIR / "safegate" / "app.py")])

def run_tests():
    print("\n[SafeGate] Đang chạy bộ kiểm thử tự động (Unit Tests)...")
    subprocess.run([str(PYTHON_EXE), "-m", "unittest", "safegate/tests/test_safegate.py"])

def print_menu():
    print("\n" + "=" * 60)
    print("   SAFEGATE - CỔNG KIỂM TRA ĐỒ BẢO HỘ LAO ĐỘNG (PPE) BẰNG AI")
    print("=" * 60)
    print("1. Chạy Cổng kiểm tra thời gian thực qua Webcam (OpenCV)")
    print("2. Mở Web Dashboard & Quản trị nhân viên (Streamlit)")
    print("3. Chạy kiểm thử tự động (Unit Tests)")
    print("4. Thoát")
    print("=" * 60)

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("--gate", "-g", "gate"):
            run_gate()
            return
        elif arg in ("--dashboard", "-d", "dashboard", "web"):
            run_dashboard()
            return
        elif arg in ("--test", "-t", "test"):
            run_tests()
            return

    while True:
        print_menu()
        choice = input("Vui lòng chọn (1-4): ").strip()
        if choice == "1":
            run_gate()
        elif choice == "2":
            run_dashboard()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            print("\nTạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng thử lại.")

if __name__ == "__main__":
    main()
