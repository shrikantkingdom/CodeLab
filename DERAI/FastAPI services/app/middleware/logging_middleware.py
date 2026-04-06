"""Structured logging middleware with request ID tracing."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request with timing, status, and a unique request ID."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.time()

        # Attach request_id to state so handlers can access it
        request.state.request_id = request_id

        response = await call_next(request)

        elapsed_ms = (time.time() - start) * 1000
        logger.info(
            "Request processed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(elapsed_ms, 2),
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
