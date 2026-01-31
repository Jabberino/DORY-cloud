"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import teams, coaches, swimmers, exercises, goals, sessions

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Cloud API for swim training pipeline with lap/stroke detection"
)

# CORS middleware for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(teams.router)
app.include_router(coaches.router)
app.include_router(swimmers.router)
app.include_router(exercises.router)
app.include_router(goals.router)
app.include_router(sessions.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.API_VERSION}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Swim Pipeline API",
        "docs": "/docs",
        "version": settings.API_VERSION
    }
