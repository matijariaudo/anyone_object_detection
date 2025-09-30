from yolo import predict_gap, predict_product
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)

while True:
    task = r.brpop("task_queue")  # espera hasta que haya tarea
    _, value = task
    data = json.loads(value.decode())  # convierte de JSON a dict
    prediction_product = predict_product(data['path'])
    prediction_gap = predict_gap(data['path'])
    result = {"output_product": prediction_product , "output_gap": prediction_gap}
    # Guardás el resultado en Redis
    r.set(data['id'], json.dumps(result))