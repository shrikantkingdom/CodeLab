"""Main API router — aggregates all endpoint routers."""

from fastapi import APIRouter

from app.api.ai_config import router as ai_config_router
from app.api.compare import router as compare_router
from app.api.health import router as health_router
from app.api.process import router as process_router

router = APIRouter()
router.include_router(health_router)
router.include_router(process_router)
router.include_router(compare_router)
router.include_router(ai_config_router)
