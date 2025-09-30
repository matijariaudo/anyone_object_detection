from ultralytics import YOLO
#DEFINIMOS EL MODELO:
# Cargando YOLOv8 preentrenado (SKU1001k)
model_product = YOLO("./models/products_model.pt")  # n = nano (rápido), también hay s, m, l, x
model_gap = YOLO("./models/gap_model.pt")  # n = nano (rápido), también hay s, m, l, x

def predict_product(img_path):
    results = model_product(img_path, classes=[0,1], conf=0.3) #PROBAR MODELO
    res = results[0]
    return res.boxes.xyxyn.tolist()

def predict_gap(img_path):
    results = model_gap(img_path, classes=[0,1], conf=0.2) #PROBAR MODELO
    res = results[0]
    return res.boxes.xyxyn.tolist()