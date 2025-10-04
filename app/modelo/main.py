from yolo import predict
import redis
import json
import os

# ==========================================
# Redis Connection (Docker-compatible)
# ==========================================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

print(f"🔴 Connecting to Redis at {REDIS_HOST}:{REDIS_PORT}...")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Test connection before starting loop
try:
    r.ping()
    print(f"✅ Connected to Redis successfully!")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

print("🔄 Starting queue processor...")

# ==========================================
# Main Processing Loop
# ==========================================
while True:
    try:
        _, value = r.brpop("task_queue")
        data = json.loads(value.decode())
        
        print(f"📥 Processing task: {data['id']}")
        
        # Run YOLO prediction
        product_boxes, gap_boxes = predict(data['path'])
        result = {"output_product": product_boxes, "output_gap": gap_boxes}
        
        # Store result in Redis
        r.set(data['id'], json.dumps(result), ex=60)  # Expire after 60 seconds
        
        print(f"✅ Task completed: {data['id']}")
        
    except Exception as e:
        print(f"❌ Error processing task: {e}")
        # Don't exit, continue processing next task