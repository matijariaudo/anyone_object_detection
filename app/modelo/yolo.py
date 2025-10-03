from ultralytics import YOLO

# cargás el modelo una vez
model = YOLO("./models/final_model.pt")
threshold_product=0.4
threshold_gap=0.25
def predict(img_path):
    results = model(img_path, conf=0.1)[0]  # umbral general bajo
    product_boxes, gap_boxes = [], []

    for box, cls, conf in zip(results.boxes.xyxyn.tolist(),
                              results.boxes.cls.tolist(),
                              results.boxes.conf.tolist()):
        if int(cls) == 1 and conf >= threshold_product:   # products con conf >= 0.3
            product_boxes.append(box)
        elif int(cls) == 0 and conf >= threshold_gap: # gaps con conf >= 0.2
            gap_boxes.append(box)

    return product_boxes, gap_boxes