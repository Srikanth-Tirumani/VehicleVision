# my_utils/database.py
import os
import sqlite3
from datetime import datetime

try:
    import mysql.connector
except ImportError:
    mysql = None

from config import DB_CONFIG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(BASE_DIR, "overload_db.sqlite")

def get_connection():
    if mysql is not None and DB_CONFIG.get("host"):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            return conn, "mysql"
        except Exception:
            pass
    conn = sqlite3.connect(SQLITE_PATH)
    return conn, "sqlite"

def init_db():
    """Initializes the database schema and performs auto-migration if needed."""
    try:
        conn, db_type = get_connection()
        cur = conn.cursor()
        if db_type == "mysql":
            cur.execute("""
            CREATE TABLE IF NOT EXISTS overloaded_vehicles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vehicle_type VARCHAR(50),
                passengers INT DEFAULT 0,
                cargo_weight FLOAT DEFAULT 0,
                violation_reason VARCHAR(255) DEFAULT '',
                photo_path VARCHAR(255) DEFAULT '',
                video_path VARCHAR(255) DEFAULT '',
                confidence FLOAT DEFAULT 0.0,
                timestamp DATETIME
            )
            """)
        else:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS overloaded_vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_type TEXT,
                passengers INTEGER DEFAULT 0,
                cargo_weight REAL DEFAULT 0,
                violation_reason TEXT DEFAULT '',
                photo_path TEXT DEFAULT '',
                video_path TEXT DEFAULT '',
                confidence REAL DEFAULT 0.0,
                timestamp DATETIME
            )
            """)
            # Check existing columns in sqlite for migration
            cur.execute("PRAGMA table_info(overloaded_vehicles)")
            cols = [row[1] for row in cur.fetchall()]
            extra_cols = [
                ("passengers", "INTEGER DEFAULT 0"),
                ("cargo_weight", "REAL DEFAULT 0"),
                ("violation_reason", "TEXT DEFAULT ''"),
                ("photo_path", "TEXT DEFAULT ''"),
                ("video_path", "TEXT DEFAULT ''"),
                ("confidence", "REAL DEFAULT 0.0"),
            ]
            for col_name, col_def in extra_cols:
                if col_name not in cols:
                    try:
                        cur.execute(f"ALTER TABLE overloaded_vehicles ADD COLUMN {col_name} {col_def}")
                    except Exception:
                        pass

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database init error: {e}")
        return False

def insert_overloaded(vehicle_type, passengers=0, cargo_weight=0.0, violation_reason="", photo_path="", video_path="", confidence=0.0):
    """Inserts a new overloaded vehicle violation incident."""
    try:
        init_db()
        conn, db_type = get_connection()
        cur = conn.cursor()
        now_dt = datetime.now()

        if db_type == "mysql":
            cur.execute("""
                INSERT INTO overloaded_vehicles 
                (vehicle_type, passengers, cargo_weight, violation_reason, photo_path, video_path, confidence, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (vehicle_type, passengers, cargo_weight, violation_reason, photo_path, video_path, confidence, now_dt))
        else:
            cur.execute("""
                INSERT INTO overloaded_vehicles 
                (vehicle_type, passengers, cargo_weight, violation_reason, photo_path, video_path, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (vehicle_type, passengers, cargo_weight, violation_reason, photo_path, video_path, confidence, now_dt.strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        conn.close()
        return last_id
    except Exception as e:
        print(f"Error inserting record: {e}")
        return None

def get_all_records(limit=200):
    """Fetches records sorted by timestamp descending."""
    init_db()
    conn, db_type = get_connection()
    records = []
    try:
        if db_type == "mysql":
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM overloaded_vehicles ORDER BY timestamp DESC LIMIT %s", (limit,))
            records = cur.fetchall()
            cur.close()
        else:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM overloaded_vehicles ORDER BY timestamp DESC LIMIT ?", (limit,))
            records = [dict(row) for row in cur.fetchall()]
            cur.close()
    except Exception as e:
        print(f"Error fetching records: {e}")
    finally:
        conn.close()
    return records

def delete_record_by_id(record_id):
    """Deletes a record and returns the deleted item details for file cleanup."""
    init_db()
    conn, db_type = get_connection()
    deleted_item = None
    try:
        if db_type == "mysql":
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM overloaded_vehicles WHERE id = %s", (record_id,))
            deleted_item = cur.fetchone()
            cur.execute("DELETE FROM overloaded_vehicles WHERE id = %s", (record_id,))
            conn.commit()
            cur.close()
        else:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM overloaded_vehicles WHERE id = ?", (record_id,))
            row = cur.fetchone()
            if row:
                deleted_item = dict(row)
            cur.execute("DELETE FROM overloaded_vehicles WHERE id = ?", (record_id,))
            conn.commit()
            cur.close()
    except Exception as e:
        print(f"Error deleting record: {e}")
    finally:
        conn.close()
    return deleted_item

def get_statistics():
    """Calculates summary KPIs and breakdown charts."""
    records = get_all_records(limit=1000)
    total_violations = len(records)
    vehicle_counts = {}
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_violations = 0

    for r in records:
        v_type = (r.get("vehicle_type") or "unknown").capitalize()
        vehicle_counts[v_type] = vehicle_counts.get(v_type, 0) + 1
        ts_val = str(r.get("timestamp", ""))
        if ts_val.startswith(today_str):
            today_violations += 1

    return {
        "total_violations": total_violations,
        "today_violations": today_violations,
        "vehicle_counts": vehicle_counts,
        "recent_records": records[:10]
    }
