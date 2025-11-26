"""
FastAPI application entry point.
University Wellbeing API - Main application setup.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import surveys

# Create FastAPI application
app = FastAPI(
    title="University Wellbeing API",
    description="API for managing and analyzing university student wellbeing data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(surveys.router)


@app.get("/", tags=["health"])
def root():
    """Root endpoint - API health check."""
    return {
        "message": "University Wellbeing API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
