import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "greenguard.db")

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Create Tables
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_id TEXT PRIMARY KEY,
                room_name TEXT NOT NULL,
                building TEXT,
                capacity INTEGER
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS room_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                person_count INTEGER,
                light_status TEXT,
                power_watts REAL,
                FOREIGN KEY(room_id) REFERENCES rooms(room_id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                message TEXT,
                resolved BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(room_id) REFERENCES rooms(room_id)
            )
        """)
        
        # Seed Default Room (optional, but helpful for prototype)
        await db.execute("""
            INSERT OR IGNORE INTO rooms (room_id, room_name, building, capacity)
            VALUES ('room_1', 'Lecture Hall 402', 'E-Block', 60)
        """)
        
        await db.commit()

async def log_room_event(room_id: str, person_count: int, light_status: str, power_watts: float):
    """Logs a state change event for a room."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO room_events (room_id, person_count, light_status, power_watts) VALUES (?, ?, ?, ?)",
            (room_id, person_count, light_status, power_watts)
        )
        await db.commit()

async def log_alert(room_id: str, alert_type: str, message: str):
    """Logs a triggered energy alert."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO alerts (room_id, alert_type, message) VALUES (?, ?, ?)",
            (room_id, alert_type, message)
        )
        await db.commit()

async def get_recent_alerts(limit=10):
    """Fetches the most recent alerts."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_room_history(room_id: str, limit=50):
    """Fetches historical state events for a specific room."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM room_events WHERE room_id = ? ORDER BY timestamp DESC LIMIT ?",
            (room_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows][::-1]  # Reverse to chronological order
