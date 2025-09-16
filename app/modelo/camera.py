import cv2
from ultralytics import YOLO

# Cargar modelo
model = YOLO("./models/products_model.pt")

def predict_frame(frame):
    # Pasar frame a YOLO
    results = model(frame, classes=[0, 1], conf=0.07)
    res = results[0]

    # Dibujar boxes sobre el frame
    for box, conf, cls in zip(res.boxes.xyxy.cpu().numpy(),
                            res.boxes.conf.cpu().numpy(),
                            res.boxes.cls.cpu().numpy()):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f"{int(cls)} {conf:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    return frame

def main():
    cap = cv2.VideoCapture(0)  # 0 = primera cámara
    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Predecir y mostrar
        frame = predict_frame(frame)
        cv2.imshow("YOLO Cam Test", frame)

        # salir con q
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
