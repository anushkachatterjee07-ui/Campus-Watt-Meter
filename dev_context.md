# 🧠 Development Context & System Architecture

## 🎯 Project Vision

Build an AI-powered energy monitoring system that:

* Uses existing CCTV (webcam simulation)
* Detects room occupancy in real time
* Flags energy wastage (lights ON + room empty)
* Provides actionable dashboard insights

---

## 🏗️ System Architecture

```
[ Webcam / CCTV ]
        ↓
[ Computer Vision Module (Python + OpenCV + YOLO) ]
        ↓
[ FastAPI Backend ]
        ↓
[ Database (optional: SQLite / MongoDB) ]
        ↓
[ React Frontend Dashboard ]
```

---

## ⚙️ Tech Stack

### 🔹 Computer Vision

* Python
* OpenCV
* YOLOv8 (Ultralytics)

### 🔹 Backend

* FastAPI
* Uvicorn
* REST APIs

### 🔹 Frontend

* React.js
* Tailwind CSS (optional)
* Chart library (Recharts / Chart.js)

---

## 🧩 Backend Responsibilities

### 1. API Endpoints

#### POST `/update-status`

* Receives CV data

#### GET `/status`

* Returns all room states

#### GET `/alerts`

* Returns energy waste alerts

---

### 2. Data Model

```json
{
  "room_id": "A101",
  "occupancy": "occupied",
  "last_updated": "timestamp",
  "light_status": "on",
  "wastage": true
}
```

---

### 3. Energy Logic

```
IF occupancy == empty AND light == ON
→ wastage = TRUE
```

---

## 🎨 Frontend Dashboard

### Features:

* Live room status grid
* Color coding:

  * 🟢 Occupied
  * 🔴 Empty + Lights ON (Wastage)
  * ⚪ Empty + Lights OFF

### Components:

* Room Card
* Status Indicator
* Alert Panel

---

## 🔄 Data Flow

1. CV detects person
2. Sends JSON → FastAPI
3. Backend updates state
4. Frontend polls `/status` every 5 sec
5. UI updates in real-time

---

## 🧪 Local Development Setup

### Backend

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

### Frontend

```bash
npm install
npm start
```

### CV Module

```bash
pip install opencv-python ultralytics requests
python detect.py
```

---

## 🧱 Folder Structure

```
project/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   └── models/
│
├── frontend/
│   ├── src/
│   └── components/
│
├── cv_module/
│   └── detect.py
│
└── docs/
    ├── COMPUTER_VISION.MD
    └── DEV_CONTEXT.MD
```

---

## ⚠️ Constraints

* Must run on low-cost hardware
* No expensive sensors
* Real-time response (<2 sec latency)

---

## 🚀 Stretch Goals

* Auto-switch lights (IoT integration)
* Historical analytics (energy savings)
* Admin panel for facility managers
* Multi-campus scaling

---

## ✅ Deliverables

* Working CV detection pipeline
* Functional backend APIs
* Live dashboard UI
* Energy wastage alerts
