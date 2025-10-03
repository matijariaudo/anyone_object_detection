import cv2
import numpy as np

# cache global de últimas imágenes por cámara
last_frames = {}

def image_differs(img_path, camera_id: int, threshold=5.0):
    """
    Compara la imagen actual con la última guardada para ese camera_id.
    Siempre actualiza el último frame.
    """
    global last_frames

    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True  # si falla la lectura, procesar igual

    last_frame = last_frames.get(camera_id)

    if last_frame is None:
        last_frames[camera_id] = img
        return True

    # Redimensionar si cambian tamaños
    if img.shape != last_frame.shape:
        last_frames[camera_id] = img
        return True

    # Diferencia absoluta
    diff = cv2.absdiff(img, last_frame)
    change = np.sum(diff > 25) / diff.size * 100

    # siempre actualizamos al último frame
    last_frames[camera_id] = img

    return change >= threshold
