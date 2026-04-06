"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from app.config import settings
from app.db.db2_connector import DB2Connector
from app.db.snowflake_connector import SnowflakeConnector
from app.models.response_models import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check service health and dependency status."""
    services: dict[str, str] = {}

    # Snowflake
    try:
        sf = SnowflakeConnector()
        services["snowflake"] = "healthy" if await sf.health_check() else "unhealthy"
    except Exception:
        services["snowflake"] = "unhealthy"

    # DB2
    try:
        db2 = DB2Connector()
        services["db2"] = "healthy" if await db2.health_check() else "unhealthy"
    except Exception:
        services["db2"] = "unhealthy"

    # Spring Boot
    import httpx
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.springboot_url}/health")
            services["springboot"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except Exception:
        services["springboot"] = "unavailable"

    overall = "healthy" if all(v != "unhealthy" for v in services.values()) else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.app_version,
        services=services,
        timestamp=datetime.utcnow(),
    )
