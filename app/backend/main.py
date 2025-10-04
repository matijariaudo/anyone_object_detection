import json
import os
import shutil
import tempfile
import time

import redis
import uvicorn
from database.functions import (
    check_password,
    delete_detection,
    get_cameras_by_user,
    get_detections,
    insert_camera,
    insert_detection,
    insert_user,
    update_camera_status,
)
from database.install import create_database
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from utils.delete_temp_file import cleanup_old_files
from utils.duplicates_control import image_differs

create_database()
app = FastAPI()

# Montar la carpeta frontend como estáticos
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

r = redis.Redis(host="redis", port=6379, db=0)
r.delete("task_queue")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()


@app.post("/test")
async def predecir(request: Request):
    body = await request.json()
    # Acá podrías usar el body si necesitas
    return JSONResponse(content={"status": 200, "prediction": True})


# @app.post("/predict")
# async def enqueue_image(file: UploadFile = File(...), camera_id: int = Form(...)):
#     # Crear archivo temporal
#     # base_tmp = tempfile.gettempdir()
#     # tmp_dir = os.path.join(base_tmp, "images")

#     SHARED_DIR = "/shared/images"
#     os.makedirs(SHARED_DIR, exist_ok=True)

#     file_name = f"{unique_id}.{ext}"
#     tmp_path = os.path.join(SHARED_DIR, file_name)

#     os.makedirs(tmp_dir, exist_ok=True)
#     print("Existe?", os.path.exists(tmp_dir))  # True si está creada
#     print("Ruta:", tmp_dir)
#     ext = file.filename.split(".")[-1]  # extensión (jpg, png, etc.)
#     unique_id = f"{camera_id}_{int(time.time())}"
#     file_name = f"{unique_id}.{ext}"
#     tmp_path = os.path.join(tmp_dir, file_name)
#     print(unique_id, "--", tmp_path)
#     with open(tmp_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 👇 chequeo antes de poner en cola si ha cambiado
#     if not image_differs(tmp_path, camera_id, threshold=5.0):
#         cleanup_old_files(camera_id)
#         return {"status": "no changes"}

#     # Preparo cola pre - servicio
#     task = {"id": file_name, "path": tmp_path}
#     if not file_name:
#         return {"status": "error", "msg": "Missing 'id' in request"}
#     r.lpush("task_queue", json.dumps(task))  # Pongo en redis

#     # Espero en cola post - servicio
#     start = time.time()
#     while time.time() - start < 3:
#         value = r.getdel(file_name)
#         if value:
#             parsed = json.loads(value.decode())  # <- parsea string a dict
#             cleanup_old_files(camera_id)  # <- Delete temp path
#             return JSONResponse(
#                 content={
#                     "status": "success",
#                     "result_product": parsed["output_product"],
#                     "result_gap": parsed["output_gap"],
#                     "file_name": file_name,
#                 }
#             )
#         time.sleep(0.1)
#     return {"status": "No results"}


@app.post("/predict")
async def enqueue_image(file: UploadFile = File(...), camera_id: int = Form(...)):
    # Crear directorio compartido
    shared_dir = "/shared/images"
    os.makedirs(shared_dir, exist_ok=True)

    # Asegurar nombre de archivo
    original_name = file.filename or "upload.jpg"
    ext = original_name.split(".")[-1] if "." in original_name else "jpg"

    # Generar nombre único
    unique_id = f"{camera_id}_{int(time.time())}"
    file_name = f"{unique_id}.{ext}"
    tmp_path = os.path.join(shared_dir, file_name)

    # Guardar archivo subido
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 👇 chequeo antes de poner en cola si ha cambiado
    if not image_differs(tmp_path, camera_id, threshold=5.0):
        cleanup_old_files(camera_id)
        return {"status": "no changes"}

    # Preparo cola pre - servicio
    task = {"id": file_name, "path": tmp_path}
    r.lpush("task_queue", json.dumps(task))  # Pongo en redis

    # Espero en cola post - servicio
    start = time.time()
    while time.time() - start < 3:
        value = r.getdel(file_name)
        if value:
            parsed = json.loads(value.decode())
            cleanup_old_files(camera_id)
            return JSONResponse(
                content={
                    "status": "success",
                    "result_product": parsed["output_product"],
                    "result_gap": parsed["output_gap"],
                    "file_name": file_name,
                }
            )
        time.sleep(0.1)

    return {"status": "No results"}


@app.post("/create_account")
async def create_account(request: Request):
    data = await request.json()
    try:
        insert_user(data["email"], data["password"], data["name"], True)
        return {"status": 200, "msg": "User created successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/login")
async def login(request: Request):
    data = await request.json()
    if check_password(data["email"], data["password"]):
        return {"status": 200, "msg": "Login successful"}
    return {"status": "error", "msg": "Invalid credentials"}


@app.post("/create_camera")
async def create_camera(request: Request):
    data = await request.json()
    try:
        insert_camera(data["user_id"], data["camera_name"], True)
        return {"status": 200, "msg": "Camera created successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/get_cameras")
async def get_cameras(request: Request):
    data = await request.json()
    try:
        cameras = get_cameras_by_user(data["user_id"])
        return {"status": 200, "cameras": cameras}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/delete_camera")
async def delete_camera(request: Request):
    data = await request.json()
    try:
        update_camera_status(data["camera_id"], False)
        return {"status": 200, "msg": "Camera disabled successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/insert_detection")
async def insert_detection_endpoint(request: Request):
    data = await request.json()
    try:
        camera_id = data["camera_id"]
        file_name = data["file_name"]
        objects = json.dumps(data.get("objects", []))  # guardamos como texto
        gaps = json.dumps(data.get("gaps", []))  # idem

        # copiar archivo a carpeta fija
        base_tmp = tempfile.gettempdir()
        tmp_path = os.path.join(base_tmp, "images", file_name)

        images_dir = os.path.join(
            os.path.dirname(__file__), "..", "frontend", "imagenes"
        )
        os.makedirs(images_dir, exist_ok=True)
        final_path = os.path.join(images_dir, file_name)

        if os.path.exists(tmp_path):
            shutil.copy2(tmp_path, final_path)

        # guardar en BD
        insert_detection(camera_id, file_name, objects, gaps)

        return {"status": 200, "msg": "Detection saved successfully", "file": file_name}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/get_detections")
async def get_detections_endpoint(request: Request):
    data = await request.json()
    try:
        camera_id = data.get("camera_id")
        detections = get_detections(camera_id)
        return {"status": 200, "detections": detections}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/delete_detection")
async def delete_detection_endpoint(request: Request):
    data = await request.json()
    try:
        delete_detection(data["detection_id"])
        return {"status": 200, "msg": "Detection deleted successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)
