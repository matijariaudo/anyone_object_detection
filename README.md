# 🛒 Supermarket Shelf Monitoring – Object Detection  

Detect missing products on supermarket shelves in real time using deep learning and containerized services.  

---

## 📂 Project Structure  

```
project-root/
│
├── app/
│   ├── frontend/    # HTML interfaces
│   ├── backend/     # API services
│   ├── redis/       # Queue & request management
│   └── modelo/      # Model inference service
│
├── training/
│   ├── dataset/     # Data collection & analysis
│   └── modelos/     # Model training & experiments
│
├── docker-compose.yml
├── .env
```

---

## 🚀 Features  

### 🖼️ Frontend  
- **Image Upload Interface**: Simple HTML form to upload images.  
- **Real-Time Capture**: Automatically captures and sends images for live detection.  

### ⚙️ Backend  
- **API Endpoints**:  
  - `POST /predict` → Send image directly to the model.  
  - `POST /check-change` → Compare with last image to optimize calls.  
- **Redis Integration**: Manages request queues for efficient processing.  

### 🔮 Model Service  
- Subscribes to Redis events.  
- Runs predictions using the trained object detection model.  

### 📊 Training  
- Dataset collection and preprocessing.  
- Model training experiments (Colab notebooks included).  

---

## 🐳 Deployment with Docker  

```bash
# Build and run all services
docker-compose up --build
```

- All environment variables are stored in `.env`.  
- Each service has its own `Dockerfile`.  

---

## 🧩 Tech Stack  

- **Frontend**: HTML, JS  
- **Backend**: Python  
- **Model**: Python, TensorFlow / PyTorch  
- **Queue**: Redis  
- **Containerization**: Docker & Docker Compose  

---

## 📌 Use Case  

This system is designed for **retail stores and supermarkets** to:  
- Detect shelf gaps in real time.  
- Optimize restocking processes.  
- Reduce out-of-stock situations.  

---

## 📥 Clone the Repository

```bash
cd your-repo
git clone https://github.com/matijariaudo/anyone_object_detection . #Important! "." open de project inside your repo
```

---

## 🔑 Contribution Rules

To keep the workflow clean and consistent:

1. Always switch to the **main** branch:
   ```bash
   git checkout main
   ```

2. Update your local **main**:
   ```bash
   git pull origin main
   ```

3. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```

4. Make your changes, then commit and push:
   ```bash
   git add .
   git commit -m "Add my new feature"
   git push origin feature/my-new-feature
   ```

5. Open a **Pull Request (PR)** on GitHub from your branch → `main`.

✅ Example:

```bash
git checkout main
git pull origin main
git checkout -b fix/login-bug
# make changes...
git add .
git commit -m "Fix login bug with session"
git push origin fix/login-bug
```

Then go to GitHub and create the PR.

---

## 📂 Backend Guidelines

For backend setup and API details, go to:

➡️ [app/backend/README.md](app/backend/README.md)


## 📜 License  

MIT License © 2025  
