import sqlite3
import bcrypt
import os,json

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
    conn.row_factory = sqlite3.Row   # 👈 cada fila como dict
    cursor = conn.cursor()

    cursor.execute("""
        SELECT camera_id, camera_name, camera_status
        FROM cameras
        WHERE user_id = ? AND camera_status=1
    """, (user_id,))
    rows = [dict(row) for row in cursor.fetchall()]  # 👈 lista de dicts
    conn.close()

    return rows


# ========================
# Detections
# ========================
def insert_detection(camera_id, file_name, objects, gaps, status=True):
    """
    Inserta una detección en la BD.
    - camera_id: id de la cámara
    - file_name: nombre de archivo de la imagen (ej. '12_1696250098.jpg')
    - objects: lista o texto con coordenadas de objetos detectados
    - gaps: lista o texto con coordenadas de gaps detectados
    """
    try:
        obj_list = json.loads(objects) if objects else []
    except:
        obj_list = []
    try:
        gap_list = json.loads(gaps) if gaps else []
    except:
        gap_list = []
        
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO detections (camera_id, object_count, gap_count, object_data, gap_data, photo_url, detection_status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        camera_id,
        len(obj_list) if obj_list else 0,
        len(gap_list) if gaps else 0,
        json.dumps(obj_list),
        json.dumps(gap_list),
        file_name,
        status
    ))
    print(camera_id,
        len(obj_list) if obj_list else 0,
        len(gap_list) if gaps else 0,
        json.dumps(obj_list),
        json.dumps(gap_list),
        file_name,
        status)
    conn.commit()
    conn.close()
# ========================
# Detections
# ========================

def get_detections(camera_id=None, limit=10):
    """
    Obtiene las detecciones como lista de dicts.
    Incluye la variación de gaps respecto al registro anterior.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # 👈 hace que fetchall devuelva filas tipo dict
    cursor = conn.cursor()

    if camera_id:
        cursor.execute("""
            SELECT detection_id, camera_id, object_count, gap_count,
                   object_data, gap_data, photo_url, detection_status,
                   (gap_count - LAG(gap_count) OVER (
                        PARTITION BY camera_id ORDER BY detection_id
                   )) AS gap_variation
            FROM detections
            WHERE camera_id = ? AND detection_status=1
            ORDER BY detection_id DESC
            LIMIT ?
        """, (camera_id, limit))
    else:
        cursor.execute("""
            SELECT detection_id, camera_id, object_count, gap_count,
                   object_data, gap_data, photo_url, detection_status,
                   (gap_count - LAG(gap_count) OVER (
                        PARTITION BY camera_id ORDER BY detection_id
                   )) AS gap_variation
            FROM detections
            WHERE detection_status=1
            ORDER BY camera_id, detection_id DESC
            LIMIT ?
        """, (limit,))

    rows = [dict(row) for row in cursor.fetchall()]  # 👈 transforma cada fila en dict
    conn.close()
    return rows


def delete_detection(detection_id):
    """
    Marca una detección como eliminada (detection_status=0).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE detections SET detection_status = 0 WHERE detection_id = ?
    """, (detection_id,))

    conn.commit()
    conn.close()