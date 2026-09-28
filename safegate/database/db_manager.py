"""
Database Manager for SafeGate
Quản lý cơ sở dữ liệu SQLite lưu trữ danh sách nhân viên và log kiểm tra PPE
Tuân thủ tiêu chí: KHÔNG LƯU ẢNH để bảo vệ quyền riêng tư.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pandas as pd
from safegate.config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Khởi tạo cấu trúc bảng SQLite và nạp dữ liệu mẫu ban đầu"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Bảng nhân viên (Employees)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_code TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    role TEXT DEFAULT 'Công nhân',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Bảng nhật ký kiểm tra (Access Logs) - TUYỆT ĐỐI KHÔNG LƯU ẢNH
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    employee_code TEXT NOT NULL,
                    employee_name TEXT,
                    department TEXT,
                    status TEXT NOT NULL CHECK(status IN ('PASS', 'FAIL')),
                    missing_items TEXT,
                    vote_score TEXT,
                    check_duration REAL DEFAULT 0.0
                )
            """)
            conn.commit()

        # Seed dữ liệu nhân viên mẫu nếu bảng còn trống
        self._seed_sample_employees()

    def _seed_sample_employees(self):
        sample_data = [
            ("NV-1001", "Nguyễn Văn An", "Thi công kết cấu", "Thợ sắt"),
            ("NV-1002", "Trần Đình Bình", "Thi công kết cấu", "Thợ cốp pha"),
            ("NV-1003", "Lê Hoàng Cường", "Cơ điện MEP", "Kỹ sư điện"),
            ("NV-1004", "Phạm Minh Đức", "Hoàn thiện xây dựng", "Thợ sơn"),
            ("NV-1005", "Vũ Thị Hạnh", "Ban an toàn HSE", "Cán bộ an toàn"),
            ("NV-1006", "Đỗ Quang Hùng", "Thi công kết cấu", "Thợ hàn"),
            ("NV-1007", "Hoàng Kim Oanh", "Ban chỉ huy công trường", "Giám sát kỹ thuật")
        ]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.executemany("""
                    INSERT OR IGNORE INTO employees (employee_code, full_name, department, role)
                    VALUES (?, ?, ?, ?)
                """, sample_data)
                conn.commit()

    def get_employee_by_code(self, employee_code: str) -> Optional[Dict]:
        """Truy vấn nhân viên bằng mã QR (employee_code)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT employee_code, full_name, department, role, created_at
                FROM employees WHERE employee_code = ?
            """, (employee_code.strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def add_employee(self, code: str, name: str, dept: str, role: str = "Công nhân") -> bool:
        """Thêm nhân viên mới"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO employees (employee_code, full_name, department, role)
                    VALUES (?, ?, ?, ?)
                """, (code.strip(), name.strip(), dept.strip(), role.strip()))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def list_employees(self) -> List[Dict]:
        """Danh sách tất cả nhân viên"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees ORDER BY employee_code ASC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_employee(self, employee_code: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM employees WHERE employee_code = ?", (employee_code,))
            conn.commit()
            return cursor.rowcount > 0

    def log_access(self, employee_code: str, employee_name: str, department: str,
                   status: str, missing_items: List[str], vote_score: str = "8/10",
                   duration: float = 0.0) -> int:
        """
        Ghi nhận kết quả kiểm tra vào database.
        Đúng tiêu chí: KHÔNG LƯU ẢNH để bảo vệ quyền riêng tư của công nhân.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        missing_str = ", ".join(missing_items) if missing_items else "Đủ đồ bảo hộ"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO access_logs (timestamp, employee_code, employee_name, department, status, missing_items, vote_score, check_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, employee_code, employee_name, department, status, missing_str, vote_score, round(duration, 2)))
            conn.commit()
            return cursor.lastrowid

    def get_logs(self, limit: int = 200, status_filter: Optional[str] = None,
                 search_keyword: Optional[str] = None) -> List[Dict]:
        """Truy vấn nhật ký kiểm tra có lọc"""
        query = "SELECT * FROM access_logs WHERE 1=1"
        params = []

        if status_filter and status_filter in ("PASS", "FAIL"):
            query += " AND status = ?"
            params.append(status_filter)

        if search_keyword:
            query += " AND (employee_code LIKE ? OR employee_name LIKE ? OR department LIKE ?)"
            kw = f"%{search_keyword.strip()}%"
            params.extend([kw, kw, kw])

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """Thống kê tổng quan hệ thống"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tổng số lần check
            cursor.execute("SELECT COUNT(*) FROM access_logs")
            total_checks = cursor.fetchone()[0]

            # Số PASS / FAIL
            cursor.execute("SELECT status, COUNT(*) FROM access_logs GROUP BY status")
            status_counts = dict(cursor.fetchall())
            pass_count = status_counts.get("PASS", 0)
            fail_count = status_counts.get("FAIL", 0)
            pass_rate = round((pass_count / total_checks * 100), 1) if total_checks > 0 else 0.0

            # Các món thiếu phổ biến nhất
            cursor.execute("""
                SELECT missing_items, COUNT(*) as cnt 
                FROM access_logs 
                WHERE status = 'FAIL' 
                GROUP BY missing_items 
                ORDER BY cnt DESC LIMIT 5
            """)
            top_violations = [dict(row) for row in cursor.fetchall()]

            # Số nhân viên đã đăng ký
            cursor.execute("SELECT COUNT(*) FROM employees")
            total_employees = cursor.fetchone()[0]

        return {
            "total_checks": total_checks,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_rate,
            "top_violations": top_violations,
            "total_employees": total_employees
        }

    def export_logs_df(self) -> pd.DataFrame:
        """Xuất DataFrame phục vụ xuất CSV / Excel"""
        with self.get_connection() as conn:
            return pd.read_sql_query("SELECT * FROM access_logs ORDER BY id DESC", conn)
