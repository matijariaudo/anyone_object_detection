import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("./models/products_model.pt")


def predict_frame(frame):
    """
    Run YOLO prediction on a single video frame and draw detection boxes.

    Args:
        frame (numpy.ndarray): The input video frame.

    Returns:
        numpy.ndarray: The frame with bounding boxes and labels drawn on it.
    """
    # Run YOLO on the frame (detecting only classes 0 and 1)
    results = model(frame, classes=[0, 1], conf=0.07)
    res = results[0]

    # Draw bounding boxes and confidence labels on the frame
    for box, conf, cls in zip(
        res.boxes.xyxy.cpu().numpy(),
        res.boxes.conf.cpu().numpy(),
        res.boxes.cls.cpu().numpy(),
    ):
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            frame,
            f"{int(cls)} {conf:.2f}",
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            2,
        )
    return frame


def main():
    """
    Open the default camera (index 0) and display live YOLO detections in real time.
    Press 'q' to quit.
    """
    cap = cv2.VideoCapture(0)  # 0 = first available camera
    if not cap.isOpened():
        print("Unable to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Predict and display YOLO detections
        frame = predict_frame(frame)
        cv2.imshow("YOLO Cam Test", frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
