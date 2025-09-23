import sqlite3
import bcrypt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "security_system.db")

def get_connection():
    return sqlite3.connect(DB_PATH)


# ========================
# Users
# ========================
def insert_user(email, password, name, status=True):
    conn = get_connection()
    cursor = conn.cursor()

    # Hash de la clave con bcrypt
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO users (email, password, name, user_status)
        VALUES (?, ?, ?, ?)
    """, (email, hashed_pw, name, status))

    conn.commit()
    conn.close()


def check_password(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_hash = row[0]
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
    return False


# ========================
# Cameras
# ========================
def insert_camera(user_id, camera_name, status=True):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cameras (user_id, camera_name, camera_status)
        VALUES (?, ?, ?)
    """, (user_id, camera_name, status))

    conn.commit()
    conn.close()


def update_camera_status(camera_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE cameras SET camera_status = ? WHERE camera_id = ?
    """, (status, camera_id))

    conn.commit()
    conn.close()


def get_cameras_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT camera_id, camera_name, camera_status
        FROM cameras
        WHERE user_id = ? AND camera_status=1
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return rows


# ========================
# Detections
# ========================
def insert_detection(camera_id, object_count, photo_url, status=True):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO detections (object_count, camera_id, photo_url, detection_status)
        VALUES (?, ?, ?, ?)
    """, (object_count, camera_id, photo_url, status))

    conn.commit()
    conn.close()
