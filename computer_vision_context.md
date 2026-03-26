# 🎥 Computer Vision Module Specification

## 🎯 Objective

Build a real-time computer vision pipeline that uses a CCTV feed (treated as a webcam) to:

1. Detect human presence in a room
2. Determine occupancy state (occupied / empty)
3. Output structured signals for backend decision-making

---

## 📌 Core Tasks

### 1. Video Input

* Source: Webcam (CCTV simulation)
* Protocol: OpenCV VideoCapture
* FPS target: 10–15 (optimized for low compute)

```python
cap = cv2.VideoCapture(0)
```

---

### 2. Human Detection

#### ✅ Recommended Model: YOLOv8 (Lightweight)

* Framework: Ultralytics YOLO
* Class filter: `person`
* Confidence threshold: 0.4–0.6

#### Alternative (if low hardware):

* Haar Cascade (less accurate)
* MobileNet SSD

---

### 3. Presence Logic

#### Define:

* `person_detected = True` if bounding boxes > 0
* Maintain a rolling buffer (last N frames)

#### Temporal Smoothing:

* Avoid flickering states
* Example:

  * If person detected in 3/5 recent frames → Occupied
  * Else → Empty

---

### 4. Occupancy State Machine

| Condition                    | State    |
| ---------------------------- | -------- |
| Person detected consistently | OCCUPIED |
| No detection for X seconds   | EMPTY    |

#### Suggested Threshold:

* Empty timeout: 10–20 seconds

---

### 5. Privacy Layer (IMPORTANT)

If a person is detected:

* Blur face or full bounding box

```python
roi = frame[y:y+h, x:x+w]
blurred = cv2.GaussianBlur(roi, (51, 51), 0)
frame[y:y+h, x:x+w] = blurred
```

---

### 6. Output Format (to Backend)

Send JSON via HTTP (FastAPI):

```json
{
  "room_id": "A101",
  "timestamp": "2026-03-27T10:30:00",
  "occupancy": "occupied",
  "person_count": 2,
  "confidence": 0.87
}
```

---

### 7. Communication

#### Method:

* REST API (POST request)
* Endpoint: `/update-status`

```python
requests.post("http://localhost:5000/update-status", json=data)
```

---

### 8. Optimization

* Resize frames (e.g., 640x480)
* Skip frames (process every 2nd frame)
* Use CPU-friendly model (YOLOv8n)

---

### 9. Error Handling

* Camera disconnect → retry loop
* Model failure → fallback to last known state

---

## 🚀 Future Enhancements

* Multi-room detection via multiple streams
* Pose detection (to detect “still but present”)
* Edge deployment on Raspberry Pi / Jetson Nano

---

## ✅ Expected Output

* Real-time occupancy detection
* Stable state transitions
* Clean JSON feed for backend
