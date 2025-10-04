import json

import redis
from yolo import predict

r = redis.Redis(host="redis", port=6379, db=0)

while True:
    _, value = r.brpop("task_queue")
    data = json.loads(value.decode())

    product_boxes, gap_boxes = predict(data["path"])
    result = {"output_product": product_boxes, "output_gap": gap_boxes}

    r.set(data["id"], json.dumps(result))
