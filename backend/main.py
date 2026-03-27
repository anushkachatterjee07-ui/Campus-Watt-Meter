from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.status import router
from database import init_db

app = FastAPI(
    title="GreenGuard AI Energy Monitor",
    description="AI-powered energy monitoring system using computer vision",
    version="1.0.0",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initializes the SQLite database on startup."""
    await init_db()


@app.get("/")
async def root():
    return {
        "app": "GreenGuard AI Energy Monitor",
        "version": "1.0.0",
        "endpoints": ["/status", "/alerts", "/stats", "/update-status", "/seed"],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
