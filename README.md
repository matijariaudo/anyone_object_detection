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

## 🤝 Contributing  

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.  

---

## 📜 License  

MIT License © 2025  
