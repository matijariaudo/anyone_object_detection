import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "security_system.db")

def create_database():
    # Conectar (crea el archivo si no existe)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        name TEXT NOT NULL,
        user_status BOOLEAN NOT NULL
    )
    """)

    # Crear tabla cameras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cameras (
        camera_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        camera_name TEXT NOT NULL,
        camera_status BOOLEAN NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)

    # Crear tabla detections
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
        object_count INTEGER NOT NULL,
        gap_count INTEGER NOT NULL,
        object_data TEXT NOT NULL,
        gap_data TEXT NOT NULL,
        camera_id INTEGER NOT NULL,
        photo_url TEXT NOT NULL,
        detection_status BOOLEAN NOT NULL,
        FOREIGN KEY (camera_id) REFERENCES cameras(camera_id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database and tables created successfully.")

if __name__ == "__main__":
    create_database()
