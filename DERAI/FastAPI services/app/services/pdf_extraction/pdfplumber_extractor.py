"""PDF extraction using pdfplumber."""

import io
import logging
from typing import Any

from app.services.pdf_extraction.base import PDFExtractor

logger = logging.getLogger(__name__)


class PdfPlumberExtractor(PDFExtractor):
    """Extract PDF content using pdfplumber library (good for tables)."""

    @property
    def engine_name(self) -> str:
        return "pdfplumber"

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        import pdfplumber  # imported here to make dependency optional

        pages_text = []
        tables = []

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

                # Also extract tables if present
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)

        raw_text = "\n".join(pages_text)
        logger.info("pdfplumber extracted %d pages, %d tables", page_count, len(tables))

        return {
            "raw_text": raw_text,
            "structured_data": {"tables": tables} if tables else {},
            "page_count": page_count,
        }
