"""DERAI FastAPI Application — Document Extraction, Review & AI.

Main entry point. Run with: uvicorn main:app --reload
"""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.logging_middleware import LoggingMiddleware

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Document comparison service: PDF extraction, AI classification, and DB validation.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Middleware (order matters: last added = first executed) ---
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routes ---
app.include_router(router)


@app.get("/health", include_in_schema=False)
async def root_health():
    """Root-level health check for Docker / load balancers."""
    return {"status": "healthy"}
