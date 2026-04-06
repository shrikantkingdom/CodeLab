"""PDF extraction using pdfminer.six with page selection support."""

import io
import logging
from typing import Any, Optional

from app.services.pdf_extraction.base import PDFExtractor

logger = logging.getLogger(__name__)


class PdfMinerExtractor(PDFExtractor):
    """Extract PDF content using pdfminer.six library.

    Supports selective page extraction via page_numbers parameter.
    """

    def __init__(self, page_numbers: Optional[list[int]] = None) -> None:
        self._page_numbers = page_numbers  # 0-indexed page numbers

    @property
    def engine_name(self) -> str:
        return "pdfminer"

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        from pdfminer.high_level import extract_pages, extract_text
        from pdfminer.layout import LAParams, LTTextContainer, LTChar, LTAnno

        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            boxes_flow=0.5,
            detect_vertical=False,
        )

        pdf_stream = io.BytesIO(pdf_bytes)

        # Get total page count first
        pages = list(extract_pages(pdf_stream, laparams=laparams))
        total_pages = len(pages)

        # Determine which pages to extract
        target_pages = self._page_numbers
        if target_pages:
            # Validate page numbers (0-indexed)
            target_pages = [p for p in target_pages if 0 <= p < total_pages]
        else:
            target_pages = list(range(total_pages))

        # Extract text from selected pages
        pages_text = []
        page_details = []

        for page_idx in target_pages:
            if page_idx < len(pages):
                page_layout = pages[page_idx]
                page_text = ""
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        page_text += element.get_text()

                pages_text.append(page_text)
                page_details.append({
                    "page_number": page_idx + 1,  # 1-indexed for display
                    "text_length": len(page_text),
                    "width": page_layout.width,
                    "height": page_layout.height,
                })

        raw_text = "\n".join(pages_text)

        logger.info(
            "pdfminer extracted %d/%d pages", len(target_pages), total_pages
        )

        return {
            "raw_text": raw_text,
            "structured_data": {},
            "page_count": total_pages,
            "pages_extracted": len(target_pages),
            "page_details": page_details,
        }
