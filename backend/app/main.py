from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.api.health import router as health_router
from app.api.investigation import router as investigation_router
from app.api.clusters import router as clusters_router
from app.core.config import settings

# Configure Loguru
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title="AI Kubernetes Agent",
        description="AI-powered Kubernetes troubleshooting agent",
        version="0.1.0",
    )

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(health_router)
    application.include_router(investigation_router)
    application.include_router(clusters_router)

    logger.info("AI Kubernetes Agent started successfully")

    return application


app = create_app()
