"""PDF extraction using Apache Tika."""

import io
import logging
from typing import Any

from app.services.pdf_extraction.base import PDFExtractor

logger = logging.getLogger(__name__)


class TikaExtractor(PDFExtractor):
    """Extract PDF content using Apache Tika (requires Tika server or jar)."""

    @property
    def engine_name(self) -> str:
        return "tika"

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        from tika import parser  # imported here to make dependency optional

        parsed = parser.from_buffer(pdf_bytes)
        raw_text = parsed.get("content", "") or ""
        metadata = parsed.get("metadata", {})
        page_count = int(metadata.get("xmpTPg:NPages", 0))

        logger.info("Tika extracted %d pages", page_count)

        return {
            "raw_text": raw_text.strip(),
            "structured_data": {"metadata": metadata},
            "page_count": page_count,
        }
