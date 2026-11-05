"""Main FastAPI application entry point for MedFlow."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    analytics,
    dashboard,
    forecasts,
    health,
    models_api,
    optimization,
    scenarios,
    simulations,
)
from backend.app.core.config import settings
from backend.app.core.database import Base, SessionLocal, engine
from backend.app.core.logging import logger, setup_logging
from backend.app.repositories.simulation_repo import seed_initial_data

# Ensure tables and seed data exist immediately
Base.metadata.create_all(bind=engine)
_db = SessionLocal()
try:
    seed_initial_data(_db)
finally:
    _db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes tables and seeds initial hospital operational profiles."""
    setup_logging()
    logger.info("MedFlow database schema verified.")
    yield
    logger.info("MedFlow application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Hospital Operations Digital Twin, Arrival Forecaster, and Constraint Optimization Engine.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
api_v1_prefix = settings.API_V1_STR
app.include_router(health.router, prefix=api_v1_prefix)
app.include_router(dashboard.router, prefix=api_v1_prefix)
app.include_router(forecasts.router, prefix=api_v1_prefix)
app.include_router(scenarios.router, prefix=api_v1_prefix)
app.include_router(simulations.router, prefix=api_v1_prefix)
app.include_router(optimization.router, prefix=api_v1_prefix)
app.include_router(analytics.router, prefix=api_v1_prefix)
app.include_router(models_api.router, prefix=api_v1_prefix)


@app.get("/")
def root():
    return {
        "message": "Welcome to MedFlow — AI-Powered Hospital Operations Digital Twin API",
        "docs_url": "/docs",
        "api_v1": "/api/v1",
        "version": settings.VERSION,
    }
