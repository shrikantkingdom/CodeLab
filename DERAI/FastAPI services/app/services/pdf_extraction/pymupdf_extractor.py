"""PDF extraction using PyMuPDF (fitz)."""

import io
import logging
from typing import Any

from app.services.pdf_extraction.base import PDFExtractor

logger = logging.getLogger(__name__)


class PyMuPDFExtractor(PDFExtractor):
    """Extract PDF content using PyMuPDF (fitz) library."""

    @property
    def engine_name(self) -> str:
        return "pymupdf"

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        import fitz  # PyMuPDF — imported here to make dependency optional

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = []

        for page in doc:
            pages_text.append(page.get_text())

        raw_text = "\n".join(pages_text)
        page_count = len(doc)
        doc.close()

        logger.info("PyMuPDF extracted %d pages", page_count)

        return {
            "raw_text": raw_text,
            "structured_data": {},  # AI classification will structure this
            "page_count": page_count,
        }
