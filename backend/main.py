from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.status import router

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


@app.get("/")
async def root():
    return {
        "app": "GreenGuard AI Energy Monitor",
        "version": "1.0.0",
        "endpoints": ["/status", "/alerts", "/stats", "/update-status", "/seed"],
    }
