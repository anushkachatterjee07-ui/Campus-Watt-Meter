"""
Integrated CV Service — runs YOLOv8 detection as a background thread
inside the FastAPI backend. Streams processed MJPEG frames and updates
room state directly (no HTTP round-trip needed).
"""

import cv2
import threading
import time
from datetime import datetime
from collections import deque

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

import state


class CVService:
    def __init__(self):
        self.running = False
        self.camera = None
        self.model = None
        self.thread = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.detection_buffer = deque(maxlen=5)
        self.current_state = "unknown"
        self.person_count = 0
        self.confidence = 0.0

        # Configuration
        self.room_id = "A101"
        self.confidence_threshold = 0.5
        self.occupied_threshold = 3   # 3 out of 5 frames
        self.frame_skip = 2
        self.target_size = (640, 480)
        self.camera_index = 0

    def start(self, camera_index=0, room_id="A101"):
        if self.running:
            return {"status": "already_running", "room_id": self.room_id}

        if not YOLO_AVAILABLE:
            return {"status": "error", "message": "ultralytics not installed. Run: pip install ultralytics"}

        self.camera_index = camera_index
        self.room_id = room_id
        self.running = True
        self.detection_buffer.clear()
        self.thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.thread.start()
        return {"status": "started", "room_id": self.room_id}

    def stop(self):
        if not self.running:
            return {"status": "already_stopped"}
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
        self.latest_frame = None
        return {"status": "stopped"}

    def _detection_loop(self):
        """Main detection loop running in background thread."""
        try:
            self.model = YOLO("yolov8n.pt")
        except Exception as e:
            print(f"[CV] Failed to load model: {e}")
            self.running = False
            return

        self.camera = cv2.VideoCapture(self.camera_index)
        if not self.camera.isOpened():
            print(f"[CV] Cannot open camera {self.camera_index}")
            self.running = False
            return

        print(f"[CV] Detection started for room {self.room_id}")

        frame_count = 0
        last_update_time = 0

        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                time.sleep(0.1)
                # Try to reopen camera
                self.camera.release()
                self.camera = cv2.VideoCapture(self.camera_index)
                continue

            frame_count += 1
            frame = cv2.resize(frame, self.target_size)

            # Only run detection on every Nth frame for performance
            if frame_count % self.frame_skip == 0:
                self._process_frame(frame)

            # Always update the streamed frame (with overlays)
            self._draw_overlay(frame)
            with self.frame_lock:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                self.latest_frame = buffer.tobytes()

            # Update backend state every 2 seconds
            now = time.time()
            if now - last_update_time >= 2:
                self._update_state()
                last_update_time = now

            time.sleep(0.033)  # ~30 fps cap

        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
        print("[CV] Detection stopped")

    def _process_frame(self, frame):
        """Run YOLO and update detection metrics on the frame."""
        results = self.model(frame, verbose=False)

        person_count = 0
        max_conf = 0.0

        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if cls == 0 and conf >= self.confidence_threshold:
                    person_count += 1
                    max_conf = max(max_conf, conf)

                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Privacy: blur detected person
                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        blurred = cv2.GaussianBlur(roi, (51, 51), 0)
                        frame[y1:y2, x1:x2] = blurred

                    # Bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"Person {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Temporal smoothing
        self.detection_buffer.append(person_count > 0)
        positives = sum(self.detection_buffer)
        self.current_state = "occupied" if positives >= self.occupied_threshold else "empty"
        self.person_count = person_count
        self.confidence = round(max_conf, 2)

    def _draw_overlay(self, frame):
        """Draw status overlay on the frame."""
        color = (0, 255, 0) if self.current_state == "occupied" else (0, 0, 255)
        cv2.putText(frame, f"Room {self.room_id} | {self.current_state.upper()}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, f"Persons: {self.person_count}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def _update_state(self):
        """Write current detection results directly into shared state."""
        timestamp = datetime.now().isoformat()
        light = state.rooms.get(self.room_id, {}).get("light_status", "on")
        wastage = self.current_state == "empty" and light == "on"

        room_data = {
            "room_id": self.room_id,
            "occupancy": self.current_state,
            "last_updated": timestamp,
            "light_status": light,
            "wastage": wastage,
            "person_count": self.person_count,
            "confidence": self.confidence,
        }
        state.rooms[self.room_id] = room_data
        state.history.append({**room_data})
        if len(state.history) > state.MAX_HISTORY:
            state.history = state.history[-state.MAX_HISTORY:]

    def get_frame(self):
        with self.frame_lock:
            return self.latest_frame

    def generate_mjpeg(self):
        """Yield MJPEG frames for StreamingResponse."""
        while self.running:
            frame = self.get_frame()
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.05)

    def get_info(self):
        return {
            "running": self.running,
            "room_id": self.room_id,
            "camera_index": self.camera_index,
            "current_state": self.current_state,
            "person_count": self.person_count,
            "confidence": self.confidence,
            "yolo_available": YOLO_AVAILABLE,
        }


# Singleton instance shared across the app
cv_service = CVService()
