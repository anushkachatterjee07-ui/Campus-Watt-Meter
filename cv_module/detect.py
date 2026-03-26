"""
GreenGuard - Computer Vision Module
Real-time occupancy detection using YOLOv8 with privacy protection.
Sends structured JSON data to the FastAPI backend.
"""

import cv2
import requests
import time
from datetime import datetime
from collections import deque

try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] ultralytics not installed. Run: pip install ultralytics")
    exit(1)

# ── Configuration ──────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000/update-status"
ROOM_ID = "A101"
CONFIDENCE_THRESHOLD = 0.5
BUFFER_SIZE = 5
OCCUPIED_THRESHOLD = 3        # 3 out of 5 frames → occupied
SEND_INTERVAL = 2             # seconds between backend updates
FRAME_SKIP = 2                # process every Nth frame
TARGET_SIZE = (640, 480)
CAMERA_INDEX = 0


def main():
    # Load YOLOv8 nano model (lightweight, CPU-friendly)
    print("[INFO] Loading YOLOv8n model...")
    model = YOLO("yolov8n.pt")

    # Open webcam / CCTV
    print(f"[INFO] Opening camera {CAMERA_INDEX}...")
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Check connection.")
        return

    detection_buffer = deque(maxlen=BUFFER_SIZE)
    frame_count = 0
    last_send_time = 0

    print(f"[INFO] Detection started for room {ROOM_ID}")
    print("[INFO] Press 'q' to quit\n")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[WARN] Camera read failed, retrying...")
            time.sleep(1)
            cap.release()
            cap = cv2.VideoCapture(CAMERA_INDEX)
            continue

        frame_count += 1

        # Skip frames for performance optimization
        if frame_count % FRAME_SKIP != 0:
            continue

        # Resize for consistent processing
        frame = cv2.resize(frame, TARGET_SIZE)

        # Run YOLO detection
        results = model(frame, verbose=False)

        # Filter for person class (class 0 in COCO dataset)
        person_count = 0
        max_confidence = 0.0

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf >= CONFIDENCE_THRESHOLD:
                    person_count += 1
                    max_confidence = max(max_confidence, conf)

                    # Privacy layer: blur detected persons
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        blurred = cv2.GaussianBlur(roi, (51, 51), 0)
                        frame[y1:y2, x1:x2] = blurred

                    # Draw bounding box on blurred region
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame, f"Person {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2,
                    )

        # Update rolling detection buffer
        detection_buffer.append(person_count > 0)

        # Temporal smoothing: require majority of recent frames
        positive_detections = sum(detection_buffer)
        current_state = "occupied" if positive_detections >= OCCUPIED_THRESHOLD else "empty"

        # Send to backend at configured interval
        current_time = time.time()
        if current_time - last_send_time >= SEND_INTERVAL:
            data = {
                "room_id": ROOM_ID,
                "timestamp": datetime.now().isoformat(),
                "occupancy": current_state,
                "person_count": person_count,
                "confidence": round(max_confidence, 2),
                "light_status": "on",  # Default; extend with light detection
            }

            try:
                response = requests.post(BACKEND_URL, json=data, timeout=2)
                wastage = response.json().get("wastage", False)
                tag = "⚠ WASTAGE" if wastage else "✓ OK"
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"{current_state.upper():8s} | "
                    f"Persons: {person_count} | "
                    f"Conf: {max_confidence:.2f} | {tag}"
                )
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Backend unreachable: {e}")

            last_send_time = current_time

        # On-screen display
        status_color = (0, 255, 0) if current_state == "occupied" else (0, 0, 255)
        cv2.putText(
            frame, f"Room {ROOM_ID} | {current_state.upper()}",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2,
        )
        cv2.putText(
            frame, f"Persons: {person_count}",
            (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
        )

        cv2.imshow(f"GreenGuard - Room {ROOM_ID}", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("\n[INFO] Detection stopped.")


if __name__ == "__main__":
    main()
