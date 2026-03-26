from pydantic import BaseModel
from typing import Optional


class RoomUpdate(BaseModel):
    """Schema for incoming CV module status updates."""
    room_id: str
    timestamp: Optional[str] = None
    occupancy: str  # "occupied" or "empty"
    person_count: int = 0
    confidence: float = 0.0
    light_status: str = "on"  # "on" or "off"


class RoomStatus(BaseModel):
    """Schema for room status response."""
    room_id: str
    occupancy: str
    last_updated: str
    light_status: str
    wastage: bool
    person_count: int
    confidence: float
