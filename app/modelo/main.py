import json
import os

import redis
from yolo import predict

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

while True:
    _, value = r.brpop("task_queue")
    data = json.loads(value.decode())

    product_boxes, gap_boxes = predict(data["path"])
    result = {"output_product": product_boxes, "output_gap": gap_boxes}

    r.set(data["id"], json.dumps(result))
