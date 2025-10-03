import glob
import os,tempfile,time

def cleanup_old_files(camera_id: int, max_age: int = 60):
    """
    Borra archivos temporales de un camera_id si son más viejos que `max_age` segundos.
    """
    base_tmp = tempfile.gettempdir()
    tmp_dir = os.path.join(base_tmp, "images")

    if not os.path.exists(tmp_dir):
        return

    now = time.time()
    pattern = os.path.join(tmp_dir, f"{camera_id}_*.*")

    for path in glob.glob(pattern):
        try:
            # el nombre es cameraId_timestamp.ext
            filename = os.path.basename(path)
            ts_str = filename.split("_")[1].split(".")[0]
            ts = int(ts_str)

            if now - ts > max_age:
                os.remove(path)
                print(f"🗑️ Borrado: {path}")
        except Exception as e:
            print(f"Error limpiando {path}: {e}")
