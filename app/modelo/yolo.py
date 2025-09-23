from ultralytics import YOLO
#DEFINIMOS EL MODELO:
# Cargando YOLOv8 preentrenado (SKU1001k)
model = YOLO("./models/products_model.pt")  # n = nano (rápido), también hay s, m, l, x

def predict_yolo(img_path):
    results = model(img_path, classes=[0,1], conf=0.3) #PROBAR MODELO
    res = results[0]
    return res.boxes.xyxyn.tolist()