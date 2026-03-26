"""Shared application state for the GreenGuard backend."""

# In-memory room storage: room_id -> room_data dict
rooms: dict[str, dict] = {}

# History of status updates for analytics
history: list[dict] = []
MAX_HISTORY = 1000
