from utils.delete_temp_file import cleanup_old_files
from utils.duplicates_control import image_differs
from database.install import create_database
from database.functions import (
    insert_user, check_password, insert_camera, get_cameras_by_user, 
    update_camera_status, get_detections , insert_detection,delete_detection
)
from fastapi import FastAPI, Request, UploadFile, File , Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import redis, json, tempfile, shutil, os, uvicorn , uuid , time


create_database()
app = FastAPI(title="Backend API", version="1.0.0")

# Configuración CORS (para Docker network)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a Redis (Compatible con Docker)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        socket_connect_timeout=5,
        decode_responses=False  # Keep as bytes for binary data
    )
    r.ping()
    print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    r.delete("task_queue")  # Clear queue on startup
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    r = None

# Montar la carpeta frontend como estáticos
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    print(f"✅ Frontend path mounted: {frontend_path}")
else:
    print(f"❌ Frontend path does not exist: {frontend_path}")

# Enrutadores

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>Backend API Running</h1><p>Frontend not found</p>")

@app.get("/health")
async def health():
    """Health check endpoint for Docker"""
    redis_status = "connected"
    try:
        if r:
            r.ping()
    except:
        redis_status = "disconnected"
    
    return {
        "status": "healthy",
        "service": "backend",
        "redis": redis_status
    }

@app.post("/test")
async def predecir(request: Request):
    body = await request.json()
    # Acá podrías usar el body si necesitas
    return JSONResponse(content={"status": 200, "prediction": True})

#r = redis.Redis(host="localhost", port=6379, db=0)
#r.delete("task_queue")
@app.post("/predict")
async def enqueue_image(file: UploadFile = File(...), camera_id: int = Form(...)):
    if not r:
        return {"status": "error", "msg": "Redis not connected"}
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
    if not image_differs(tmp_path,camera_id, threshold=5.0):
        cleanup_old_files(camera_id)
        return {"status": "no changes"}
    
    #Preparo cola pre - servicio
    task = {"id": file_name, "path": tmp_path}
    if not file_name:
        return {"status": "error", "msg": "Missing 'id' in request"}
    r.lpush("task_queue", json.dumps(task)) #Pongo en redis
    print(f"🖼️ Imagen {file_name} en cola para ser procesada.")
    
    #Espero en cola post - servicio
    start = time.time()
    timeout = 30  
    while time.time() - start < timeout:
        value = r.getdel(file_name)
        if value:
            parsed = json.loads(value.decode()) # <- parsea string a dict
            cleanup_old_files(camera_id)        # <- Delete temp path
            return JSONResponse(content={
                "status": "success",
                "result_product": parsed["output_product"],
                "result_gap": parsed["output_gap"],
                "file_name":file_name
            })
        time.sleep(0.1)
    
    print(f"⏰ Tiempo de espera terminado para: {file_name}")
    return {"status": "No results", "msg": "Sin respuesta durante el tiempo de espera"}

@app.post("/create_account")
async def create_account(request: Request):
    """Crear una nueva cuenta de usuario"""
    print("=" * 50)
    print("📥 Received create_account request")
    print(f"Headers: {request.headers}")
    
    # Get raw body
    body_bytes = await request.body()
    print(f"Raw body (bytes): {body_bytes}")
    print(f"Raw body (decoded): {body_bytes.decode()}")
    print("=" * 50)
    
    # Now try to parse JSON
    try:
        data = await request.json()
        print(f"✅ Parsed JSON: {data}")
    except Exception as e:
        print(f"❌ JSON parse error: {e}")
        return {"status": "error", "msg": f"Invalid JSON: {str(e)}"}
    try:
        insert_user(data["email"], data["password"], data["name"], True)
        return {"status": 200, "msg": "User created successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/login")
async def login(request: Request):
    """Verificar credenciales de usuario"""
    data = await request.json()
    if check_password(data["email"], data["password"]):
        return {"status": 200, "msg": "Login successful"}
    return {"status": "error", "msg": "Invalid credentials"}


@app.post("/create_camera")
async def create_camera(request: Request):
    """Crear una nueva cámara para un usuario"""
    data = await request.json()
    try:
        insert_camera(data["user_id"], data["camera_name"], True)
        return {"status": 200, "msg": "Camera created successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/get_cameras")
async def get_cameras(request: Request):
    """Obtener cámaras asociadas a un usuario"""
    data = await request.json()
    try:
        cameras = get_cameras_by_user(data["user_id"])
        return {"status": 200, "cameras": cameras}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/delete_camera")
async def delete_camera(request: Request):
    """Deshabilitar una cámara (soft delete)"""
    data = await request.json()
    try:
        update_camera_status(data["camera_id"], False)
        return {"status": 200, "msg": "Camera disabled successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

@app.post("/insert_detection")
async def insert_detection_endpoint(request: Request):
    """Guardar una detección en la base de datos"""
    data = await request.json()
    try:
        camera_id = data["camera_id"]
        file_name = data["file_name"]
        objects = json.dumps(data.get("objects", []))  # guardamos como texto
        gaps = json.dumps(data.get("gaps", []))          # idem

        # copiar archivo a carpeta fija
        base_tmp = tempfile.gettempdir()
        tmp_path = os.path.join(base_tmp, "images", file_name)

        images_dir = os.path.join(os.path.dirname(__file__), "..", "frontend","imagenes")
        os.makedirs(images_dir, exist_ok=True)
        final_path = os.path.join(images_dir, file_name)

        if os.path.exists(tmp_path):
            shutil.copy2(tmp_path, final_path)
            print(f"📁 Imagen movida a: {final_path}")

        # guardar en BD
        insert_detection(camera_id, file_name, objects, gaps)

        return {"status": 200, "msg": "Detection saved successfully", "file": file_name}
    except Exception as e:
        print(f"❌ Error guardando detección: {e}")
        return {"status": "error", "msg": str(e)}
    
@app.post("/get_detections")
async def get_detections_endpoint(request: Request):
    """Obtener detecciones para una cámara"""
    data = await request.json()
    try:
        camera_id = data.get("camera_id")
        detections = get_detections(camera_id)
        return {"status": 200, "detections": detections}
    except Exception as e:
        return {"status": "error", "msg": str(e)}
    
@app.post("/delete_detection")
async def delete_detection_endpoint(request: Request):
    """Eliminar una detección por ID"""
    data = await request.json()
    try:
        delete_detection(data["detection_id"])
        return {"status": 200, "msg": "Detection deleted successfully"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    """Acciones al iniciar el servidor"""
    print("=" * 50)
    print("🚀 Backend API is iniciando...")
    print(f"📁 Ruta Frontend: {frontend_path}")
    print(f"🔴 Redis: {REDIS_HOST}:{REDIS_PORT}")
    print("=" * 50)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

