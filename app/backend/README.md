# ⚡ Backend Service

This backend serves the **frontend HTML** and provides a **prediction API**.

## 📦 Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Run the Server

```bash
python main.py
```

- The app will be available at **http://localhost:9000/**
- It serves:
  - `index.html` from the frontend folder
  - `POST /predecir` → returns JSON with a prediction

## 🖥️ Endpoints

- **GET /** → renders `index.html`  
- **POST /predecir** → returns:
  ```json
  {
    "status": 200,
    "prediction": true
  }
  ```
