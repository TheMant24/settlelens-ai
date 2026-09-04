"""FastAPI application entry point for SettleLens AI"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .api.investigate import router as investigate_router
from .database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SettleLens AI",
    description="AI-powered fintech settlement investigation agent",
    version="1.0.0",
)

# CORS configuration for React frontend
# Allow common development origins
allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(investigate_router)


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "SettleLens AI",
        "status": "healthy",
        "version": "1.0.0",
        "endpoints": {
            "investigate": "POST /investigate",
            "health": "GET /health",
        },
    }


@app.get("/health")
def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "service": "settlelens-backend",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("BACKEND_HOST", "0.0.0.0"),
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
    )