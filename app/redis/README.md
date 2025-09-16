# 📦 Redis in this Project

This project uses **Redis** as a **message queue** to coordinate between the **backend (FastAPI)** and the **AI models service**.

---

## ⚙️ What does Redis do?

- 📨 **Task Queue** → The backend pushes requests into the queue (`task_queue`).  
- 🤖 **Model Worker** → The models service listens to the queue, processes tasks, and stores results.  
- 🔄 **Backend** → Reads results from Redis and returns them to the frontend.  

👉 Redis acts as the **intermediary** to ensure tasks are processed asynchronously and reliably.

---

## 🐳 How to Run Redis

You already have a `docker-compose.yml` with Redis.  
To start it:

```bash
docker compose up -d
```

This will:  
- Download the official `redis:7` image  
- Create the container `redis_server`  
- Expose port **6379** on your machine  

---

## 🔍 Verify Redis is Running

You can enter the container and use the CLI client:

```bash
docker exec -it redis_server redis-cli
```

Inside the CLI, try:

```redis
SET test "hello"
GET test
```

You should see:

```
"hello"
```

---

## 📂 Project Flow

1. **Frontend** 👉 sends a request to the backend.  
2. **Backend (FastAPI)** 👉 pushes the task into Redis.  
3. **Model Worker** 👉 consumes the task, runs the AI model, and stores the result.  
4. **Backend** 👉 fetches the result and returns it to the frontend.  

---

✨ With Redis, you have the **processing queue engine** ready.
