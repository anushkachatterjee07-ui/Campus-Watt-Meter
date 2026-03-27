from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime
from models.room import RoomUpdate
import state
from cv_service import cv_service
from logic_engine import logic_engine
from database import log_room_event, log_alert, get_room_history, get_recent_alerts

router = APIRouter()


@router.post("/update-status")
async def update_status(data: RoomUpdate):
    """Receive occupancy data from the CV module."""
    timestamp = data.timestamp or datetime.now().isoformat()
    
    # 1. Structure the current data state
    room_data = {
        "room_id": data.room_id,
        "occupancy": data.occupancy,
        "last_updated": timestamp,
        "light_status": data.light_status,
        "person_count": data.person_count,
        "confidence": round(data.confidence, 2),
        "appliance_power_watts": data.appliance_power_watts,
    }

    # 2. Evaluate system state against predefined rules (Logic Engine)
    is_wastage, alerts = logic_engine.evaluate_state(room_data)
    room_data["wastage"] = is_wastage
    room_data["triggered_alerts"] = [a[0] for a in alerts] # Names for internal state
    state.rooms[data.room_id] = room_data

    # Log to SQLite
    await log_room_event(
        data.room_id, 
        data.person_count, 
        data.light_status, 
        data.appliance_power_watts
    )
    
    # Log specific alerts to the 'alerts' table
    for alert_type, message in alerts:
        await log_alert(data.room_id, alert_type, message)

    # Track in-memory history
    state.history.append({**room_data})
    if len(state.history) > state.MAX_HISTORY:
        state.history = state.history[-state.MAX_HISTORY:]

    return {"status": "ok", "wastage": is_wastage}


@router.get("/status")
async def get_status():
    """Return current status of all monitored rooms."""
    return list(state.rooms.values())


@router.get("/alerts")
async def get_alerts():
    """Return recent historical alerts from the database."""
    return await get_recent_alerts(limit=15)


@router.get("/history/{room_id}")
async def get_history(room_id: str):
    """Return historical trend data for a specific room."""
    return await get_room_history(room_id)


@router.get("/stats")
async def get_stats():
    """Return summary statistics."""
    all_rooms = list(state.rooms.values())
    total = len(all_rooms)
    occupied = sum(1 for r in all_rooms if r["occupancy"] == "occupied")
    empty = sum(1 for r in all_rooms if r["occupancy"] == "empty")
    wastage = sum(1 for r in all_rooms if r["wastage"])
    efficient = total - wastage

    return {
        "total_rooms": total,
        "occupied": occupied,
        "empty": empty,
        "wastage_count": wastage,
        "efficient_count": efficient,
        "efficiency_rate": round((efficient / total * 100) if total > 0 else 100, 1),
    }


@router.patch("/toggle-light/{room_id}")
async def toggle_light(room_id: str):
    """Toggle the light status of a room (for testing/demo)."""
    if room_id not in state.rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room = state.rooms[room_id]
    room["light_status"] = "off" if room["light_status"] == "on" else "on"
    
    # Re-evaluate logic rules
    is_wastage, alerts = logic_engine.evaluate_state(room)
    room["wastage"] = is_wastage
    room["triggered_alerts"] = [a[0] for a in alerts]
    
    # Log alert if triggered by manual toggle
    for alert_type, message in alerts:
        await log_alert(room_id, alert_type, message)
    
    room["last_updated"] = datetime.now().isoformat()
    return room


@router.post("/seed")
async def seed_data():
    """Seed demo data for testing the dashboard."""
    demo_rooms = [
        {"room_id": "A101", "occupancy": "occupied", "light_status": "on",
         "person_count": 3, "confidence": 0.92},
        {"room_id": "A102", "occupancy": "empty", "light_status": "on",
         "person_count": 0, "confidence": 0.0},
        {"room_id": "A103", "occupancy": "occupied", "light_status": "on",
         "person_count": 1, "confidence": 0.85},
        {"room_id": "B201", "occupancy": "empty", "light_status": "off",
         "person_count": 0, "confidence": 0.0},
        {"room_id": "B202", "occupancy": "empty", "light_status": "on",
         "person_count": 0, "confidence": 0.0},
        {"room_id": "B203", "occupancy": "occupied", "light_status": "on",
         "person_count": 2, "confidence": 0.78},
        {"room_id": "C301", "occupancy": "empty", "light_status": "off",
         "person_count": 0, "confidence": 0.0},
        {"room_id": "C302", "occupancy": "occupied", "light_status": "on",
         "person_count": 1, "confidence": 0.91},
    ]

    for room in demo_rooms:
        timestamp = datetime.now().isoformat()
        room_data_dict = {
            "room_id": room["room_id"],
            "occupancy": room["occupancy"],
            "last_updated": timestamp,
            "light_status": room["light_status"],
            "person_count": room["person_count"],
            "confidence": room["confidence"],
            "appliance_power_watts": 0.0,
        }
        
        # Evaluate Logic Engine rules
        is_wastage, alerts = logic_engine.evaluate_state(room_data_dict)
        room_data_dict["wastage"] = is_wastage
        room_data_dict["triggered_alerts"] = [a[0] for a in alerts]
        
        # Log to DB for seeded wastage
        for alert_type, message in alerts:
            await log_alert(room["room_id"], alert_type, message)
        
        state.rooms[room["room_id"]] = room_data_dict

    return {"status": "seeded", "rooms_created": len(demo_rooms)}


# ── CV Module Integration ────────────────────────────────────


@router.post("/cv/start")
async def start_cv(camera_index: int = 1, room_id: str = "A101"):
    """Start the integrated CV detection service."""
    result = cv_service.start(camera_index=camera_index, room_id=room_id)
    return result


@router.post("/cv/stop")
async def stop_cv():
    """Stop the integrated CV detection service."""
    result = cv_service.stop()
    return result


@router.post("/cv/calibrate")
async def calibrate_cv():
    """Trigger a brightness baseline calibration."""
    result = cv_service.calibrate()
    return result


@router.get("/cv/status")
async def cv_status():
    """Get current CV service status and detection info."""
    return cv_service.get_info()


@router.get("/video-feed")
async def video_feed():
    """Stream live MJPEG video from the camera with detection overlays."""
    if not cv_service.running:
        raise HTTPException(status_code=503, detail="CV service not running. POST /cv/start first.")
    return StreamingResponse(
        cv_service.generate_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
