"""PDF extraction via Spring Boot service (Pegbox / PDFBox)."""

import base64
import logging
from typing import Any

import httpx

from app.config import settings
from app.services.pdf_extraction.base import PDFExtractor

logger = logging.getLogger(__name__)


class SpringBootExtractor(PDFExtractor):
    """Delegates PDF extraction to the Spring Boot Java service.

    Sends PDF bytes (base64-encoded) to /extract/pdf and returns structured result.
    """

    def __init__(self, engine: str = "pegbox") -> None:
        self._engine = engine  # pegbox or pdfbox

    @property
    def engine_name(self) -> str:
        return self._engine

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        url = f"{settings.springboot_url}/extract/pdf"
        payload = {
            "pdfContent": base64.b64encode(pdf_bytes).decode("utf-8"),
            "engine": self._engine,
        }
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": settings.api_key,
        }

        logger.info("Calling Spring Boot extraction service (engine=%s)", self._engine)

        async with httpx.AsyncClient(timeout=settings.springboot_timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

        return {
            "raw_text": data.get("rawText", ""),
            "structured_data": data.get("extractedData", {}),
            "page_count": data.get("pageCount", 0),
        }
