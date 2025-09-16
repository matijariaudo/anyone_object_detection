from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import redis, json, tempfile, shutil, os, uvicorn , uuid , time

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
async def enqueue_image(file: UploadFile = File(...)):
    
    # Crear archivo temporal
    tmp_dir = tempfile.mkdtemp()
    ext = file.filename.split(".")[-1]  # extensión (jpg, png, etc.)
    unique_id = f"{int(time.time())}_{uuid.uuid4().hex}"
    file_name=f"{unique_id}.{ext}"
    tmp_path = os.path.join(tmp_dir, file_name)
    print(unique_id,"--",tmp_path)
    with open(tmp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    task = {"id": file_name, "path": tmp_path}
    if not file_name:
        return {"status": "error", "msg": "Missing 'id' in request"}
    print("Queued Data")
    #return {"status": "No results", "data": json.dumps(task)}
    r.lpush("task_queue", json.dumps(task))
    
    start = time.time()
    while time.time() - start < 3:
        value = r.getdel(file_name)
        if value:
            parsed = json.loads(value.decode()) # <- parsea string a dict
            shutil.rmtree(tmp_dir)              # <- Delete temp path
            return JSONResponse(content={"status": 200, "result": parsed["output"]})
        time.sleep(0.1)

    return {"status": "No results"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9000, reload=True)
