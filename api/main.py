"""
Main FastAPI Application for the OpenKarotz On-Device API

This file initializes the FastAPI application and includes the modular routers
that define the API's endpoints.
"""

from fastapi import FastAPI
from .routers import system, rfid, media, tts, management, tools

app = FastAPI(
    title="OpenKarotz Modern API",
    description="A modern, on-device API for the OpenKarotz, replacing the legacy cgi-bin scripts.",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# --- Root Endpoint ---
@app.get("/api", tags=["Root"])
def read_root():
    """
    A welcome message to confirm the API is running.
    """
    return {"message": "Welcome to the OpenKarotz Modern API"}

# --- Include Routers ---
# The application is composed of modular routers for each functional area.
app.include_router(system.router, prefix="/api")

# Placeholder for future routers:
app.include_router(rfid.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(tts.router, prefix="/api")
app.include_router(management.router, prefix="/api")
app.include_router(tools.router, prefix="/api")