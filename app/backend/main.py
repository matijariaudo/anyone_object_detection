from utils.duplicates_control import image_differs
from database.install import create_database
from database.functions import insert_user, check_password, insert_camera, get_cameras_by_user, update_camera_status
from fastapi import FastAPI, Request, UploadFile, File , Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import redis, json, tempfile, shutil, os, uvicorn , uuid , time

create_database()
app = FastAPI()

# Montar la carpeta frontend como estáticos
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

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

r = redis.Redis(host="localhost", port=6379, db=0)
@app.post("/predict")
async def enqueue_image(file: UploadFile = File(...), camera_id: int = Form(...)):
    # Crear archivo temporal
    base_tmp = tempfile.gettempdir()
    tmp_dir = os.path.join(base_tmp, "images")
    os.makedirs(tmp_dir, exist_ok=True)
    print("Existe?", os.path.exists(tmp_dir))   # True si está creada
    print("Ruta:", tmp_dir)
    ext = file.filename.split(".")[-1]  # extensión (jpg, png, etc.)
    unique_id = f"{camera_id}_{int(time.time())}"
    file_name=f"{unique_id}.{ext}"
    tmp_path = os.path.join(tmp_dir, file_name)
    print(unique_id,"--",tmp_path)
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 👇 chequeo antes de poner en cola si ha cambiado
    if not image_differs(tmp_path, threshold=5.0):
        shutil.rmtree(tmp_dir)
        return {"status": "no changes"}
    
    #Preparo cola pre - servicio
    task = {"id": file_name, "path": tmp_path}
    if not file_name:
        return {"status": "error", "msg": "Missing 'id' in request"}
    r.lpush("task_queue", json.dumps(task)) #Pongo en redis
    
    #Espero en cola post - servicio
    start = time.time()
    while time.time() - start < 3:
        value = r.getdel(file_name)
        if value:
            parsed = json.loads(value.decode()) # <- parsea string a dict
            shutil.rmtree(tmp_dir)              # <- Delete temp path
            return JSONResponse(content={"status": "success", "result_product": parsed["output_product"], "result_gap": parsed["output_gap"]})
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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)

