from yolo import predict_yolo
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)

while True:
    task = r.brpop("task_queue")  # espera hasta que haya tarea
    _, value = task
    data = json.loads(value.decode())  # convierte de JSON a dict
    print("Procesando:", data)

    prediction = predict_yolo(data['path'])
    result = {"output": prediction}
    # Guardás el resultado en Redis
    r.set(data['id'], json.dumps(result))