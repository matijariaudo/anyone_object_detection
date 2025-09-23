import cv2
import numpy as np

last_frame = None  # global cache en memoria

def image_differs(img_path, threshold=5.0):
    global last_frame
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return True  # si falla la lectura, procesar igual

    if last_frame is None:
        last_frame = img
        return True

    # Redimensionar si cambian tamaños
    if img.shape != last_frame.shape:
        last_frame = img
        return True

    # Diferencia absoluta
    diff = cv2.absdiff(img, last_frame)
    change = np.sum(diff > 25) / diff.size * 100

    if change >= threshold:
        last_frame = img
        return True
    else:
        return False
