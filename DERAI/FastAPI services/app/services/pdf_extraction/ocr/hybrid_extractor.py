"""Hybrid OCR Extractor — per-page engine selection.

This is the key differentiator: users can choose OCR only for pages
containing images, while text-heavy pages use faster standard extractors.
Results from all pages are integrated into a single unified output.

Architecture:
  1. Convert PDF → individual page images (via PyMuPDF)
  2. Classify each page: text-dominant vs image-dominant
  3. Route text pages → user-selected text extractor (pdfminer/pdfplumber/pymupdf)
  4. Route image pages → OCR extractor (pytesseract/Azure Doc Intelligence)
  5. Merge all page results in order → unified extraction output
"""

import io
import logging
from typing import Any

from app.services.pdf_extraction.base import PDFExtractor
from app.services.pdf_extraction.ocr.base_ocr import OCREngine, OCRExtractor
from app.services.pdf_extraction.ocr.pytesseract_extractor import PytesseractExtractor
from app.services.pdf_extraction.ocr.azure_doc_intelligence import AzureDocIntelligenceExtractor

logger = logging.getLogger(__name__)


class OCRExtractorFactory:
    """Factory for creating OCR engine instances."""

    @staticmethod
    def create(engine: OCREngine, **kwargs) -> OCRExtractor:
        engines = {
            OCREngine.PYTESSERACT: PytesseractExtractor,
            OCREngine.AZURE_DOC_INTELLIGENCE: AzureDocIntelligenceExtractor,
        }
        cls = engines.get(engine)
        if cls is None:
            raise ValueError(f"Unsupported OCR engine: {engine}. Available: {list(engines.keys())}")

        # Auto-inject Azure credentials from config if not provided
        if engine == OCREngine.AZURE_DOC_INTELLIGENCE and "endpoint" not in kwargs:
            from app.config import settings
            kwargs.setdefault("endpoint", settings.azure_doc_endpoint)
            kwargs.setdefault("api_key", settings.azure_doc_api_key)
            kwargs.setdefault("model_id", settings.azure_doc_model)

        return cls(**kwargs)


class HybridOCRExtractor(PDFExtractor):
    """Hybrid page-level extraction: text pages use a standard extractor,
    image pages use an OCR extractor. Results are merged in page order.

    The text extractor for non-image pages is configurable:
      - 'pdfminer' (default) — layout-aware, best for structured docs
      - 'pymupdf'  — fast, general purpose
      - 'pdfplumber' — good for table-heavy pages

    Usage:
        extractor = HybridOCRExtractor(
            ocr_engine=OCREngine.PYTESSERACT,
            text_engine_name="pdfminer",
            ocr_all_pages=False,
        )
        result = await extractor.extract(pdf_bytes)
    """

    def __init__(
        self,
        text_extractor: PDFExtractor | None = None,
        ocr_engine: OCREngine = OCREngine.PYTESSERACT,
        ocr_kwargs: dict | None = None,
        ocr_all_pages: bool = False,
        image_text_ratio_threshold: float = 0.3,
        text_engine_name: str = "pdfminer",
    ):
        """
        Args:
            text_extractor: Explicit PDFExtractor instance for text-heavy pages.
                           If provided, text_engine_name is ignored.
            ocr_engine: Which OCR engine to use for image pages.
            ocr_kwargs: Extra kwargs passed to OCR engine constructor.
            ocr_all_pages: If True, OCR every page (ignore detection).
            image_text_ratio_threshold: Pages with text coverage below this
                                        ratio are considered image-dominant.
            text_engine_name: Name of text engine for non-image pages
                             ('pdfminer', 'pymupdf', 'pdfplumber').
        """
        self._text_extractor = text_extractor
        self._ocr_engine = ocr_engine
        self._ocr_kwargs = ocr_kwargs or {}
        self._ocr_all_pages = ocr_all_pages
        self._threshold = image_text_ratio_threshold
        self._text_engine_name = text_engine_name
        self._ocr_extractor = OCRExtractorFactory.create(ocr_engine, **self._ocr_kwargs)

    @property
    def engine_name(self) -> str:
        return f"hybrid_{self._ocr_engine.value}+{self._text_engine_name}"

    def _get_text_extractor(self) -> PDFExtractor:
        """Get or build the text extractor for non-image pages."""
        if self._text_extractor is not None:
            return self._text_extractor
        # Lazy import to avoid circular deps
        from app.services.pdf_extraction.pdfminer_extractor import PdfMinerExtractor
        from app.services.pdf_extraction.pymupdf_extractor import PyMuPDFExtractor
        from app.services.pdf_extraction.pdfplumber_extractor import PdfPlumberExtractor

        engines = {
            "pdfminer": PdfMinerExtractor,
            "pymupdf": PyMuPDFExtractor,
            "pdfplumber": PdfPlumberExtractor,
        }
        cls = engines.get(self._text_engine_name, PdfMinerExtractor)
        return cls()

    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        """Extract content from PDF using hybrid page-level strategy.

        Each page is auto-classified as text-dominant or image-dominant.
        Text pages → standard extractor. Image pages → OCR engine.
        Returns rich per-page metadata for the debug panel.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            logger.error("PyMuPDF required for hybrid OCR extraction")
            return {"raw_text": "", "structured_data": {}, "page_count": 0}

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        all_text_parts: list[str] = []
        page_results: list[dict[str, Any]] = []
        ocr_pages: list[tuple[int, bytes]] = []
        text_pages: list[tuple[int, int]] = []  # (page_num, _placeholder)
        page_classifications: dict[int, dict[str, Any]] = {}

        # --- Phase 1: Classify every page ---
        for page_num in range(page_count):
            page = doc[page_num]
            classification = self._classify_page(page)
            page_classifications[page_num] = classification
            is_image = self._ocr_all_pages or classification["is_image_dominant"]

            if is_image:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                ocr_pages.append((page_num, img_bytes))
                reason = "force_all" if self._ocr_all_pages else classification["reason"]
                logger.info(
                    "Page %d → OCR (%s) | text=%d chars, images=%d, coverage=%.1f%%, reason=%s",
                    page_num + 1, self._ocr_engine.value,
                    classification["text_chars"], classification["image_count"],
                    classification["image_coverage_pct"] * 100, reason,
                )
            else:
                text_pages.append((page_num, 0))
                logger.info(
                    "Page %d → text extractor (%s) | text=%d chars, images=%d",
                    page_num + 1, self._text_engine_name,
                    classification["text_chars"], classification["image_count"],
                )

        # --- Phase 2: Run OCR on image pages ---
        ocr_results: dict[int, dict[str, Any]] = {}
        if ocr_pages:
            image_bytes_list = [img for _, img in ocr_pages]
            results = await self._ocr_extractor.extract_from_images_batch(image_bytes_list)
            for (page_num, _), result in zip(ocr_pages, results):
                ocr_results[page_num] = result

        # --- Phase 3: Extract text from non-image pages ---
        text_page_results: dict[int, str] = {}
        if text_pages:
            text_page_nums = [pn for pn, _ in text_pages]
            if self._text_engine_name == "pdfminer":
                from app.services.pdf_extraction.pdfminer_extractor import PdfMinerExtractor
                for pn in text_page_nums:
                    single = PdfMinerExtractor(page_numbers=[pn])
                    single_result = await single.extract(pdf_bytes)
                    text_page_results[pn] = single_result["raw_text"]
            else:
                for pn in text_page_nums:
                    text_page_results[pn] = doc[pn].get_text()

        # --- Phase 4: Merge results in page order ---
        for page_num in range(page_count):
            cls_info = page_classifications.get(page_num, {})
            base_detail = {
                "page": page_num + 1,
                "is_image_dominant": cls_info.get("is_image_dominant", False),
                "image_count": cls_info.get("image_count", 0),
                "image_coverage_pct": round(cls_info.get("image_coverage_pct", 0) * 100, 1),
                "raw_text_chars": cls_info.get("text_chars", 0),
                "text_density": round(cls_info.get("text_density", 0), 4),
                "detection_reason": cls_info.get("reason", "text_page"),
            }

            if page_num in ocr_results:
                ocr_result = ocr_results[page_num]
                page_text = ocr_result["text"]
                all_text_parts.append(page_text)
                base_detail.update({
                    "method": "ocr",
                    "engine": self._ocr_engine.value,
                    "confidence": ocr_result.get("confidence", 0.0),
                    "text_length": len(page_text),
                    "extracted_text": page_text,
                })
            elif page_num in text_page_results:
                text = text_page_results[page_num]
                all_text_parts.append(text)
                base_detail.update({
                    "method": "text",
                    "engine": self._text_engine_name,
                    "confidence": 1.0,
                    "text_length": len(text),
                    "extracted_text": text,
                })

            page_results.append(base_detail)

        doc.close()
        full_text = "\n\n".join(all_text_parts)

        logger.info(
            "Hybrid extraction complete: %d pages (%d text via %s, %d OCR via %s), total %d chars",
            page_count, len(text_pages), self._text_engine_name,
            len(ocr_pages), self._ocr_engine.value, len(full_text),
        )

        return {
            "raw_text": full_text,
            "structured_data": {},
            "page_count": page_count,
            "ocr_metadata": {
                "total_pages": page_count,
                "ocr_pages": len(ocr_pages),
                "text_pages": len(text_pages),
                "ocr_engine": self._ocr_engine.value,
                "text_engine": self._text_engine_name,
                "page_details": page_results,
            },
        }

    def _classify_page(self, page) -> dict[str, Any]:
        """Classify a page and return detailed detection metadata."""
        text = page.get_text()
        text_length = len(text.strip())
        rect = page.rect
        page_area = rect.width * rect.height
        images = page.get_images(full=True)

        # Calculate image coverage
        image_coverage = 0.0
        if images and page_area > 0:
            total_image_area = 0.0
            try:
                for img in page.get_image_info():
                    bbox = img.get("bbox", (0, 0, 0, 0))
                    w = abs(bbox[2] - bbox[0])
                    h = abs(bbox[3] - bbox[1])
                    total_image_area += w * h
                image_coverage = total_image_area / page_area
            except Exception:
                pass

        text_density = text_length / (page_area / 1000) if page_area > 0 else 0.0

        # Detection logic with reason tracking
        is_image = False
        reason = "text_page"

        if text_length < 50 and len(images) > 0:
            is_image = True
            reason = "low_text_with_images"
        elif image_coverage > 0.4:
            is_image = True
            reason = "high_image_coverage"
        elif page_area > 0 and text_density < self._threshold:
            is_image = True
            reason = "low_text_density"

        return {
            "is_image_dominant": is_image,
            "reason": reason,
            "text_chars": text_length,
            "image_count": len(images),
            "image_coverage_pct": image_coverage,
            "text_density": text_density,
        }
