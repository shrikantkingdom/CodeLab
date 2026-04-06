"""Factory for selecting PDF extraction engine (Strategy pattern)."""

from typing import Callable, Union

from app.models.enums import ExtractionEngine
from app.services.pdf_extraction.base import PDFExtractor
from app.services.pdf_extraction.pymupdf_extractor import PyMuPDFExtractor
from app.services.pdf_extraction.pdfplumber_extractor import PdfPlumberExtractor
from app.services.pdf_extraction.tika_extractor import TikaExtractor
from app.services.pdf_extraction.springboot_extractor import SpringBootExtractor
from app.services.pdf_extraction.pdfminer_extractor import PdfMinerExtractor
from app.services.pdf_extraction.ocr.base_ocr import OCREngine
from app.services.pdf_extraction.ocr.hybrid_extractor import HybridOCRExtractor


class ExtractorFactory:
    """Returns the appropriate PDFExtractor based on engine selection.

    To add a new engine:
      1. Create a class implementing PDFExtractor.
      2. Register it in the _ENGINES map below.

    Supports standard, OCR, and hybrid extraction modes:
      - Standard: PyMuPDF, pdfplumber, Tika, Pegbox, PDFBox
      - OCR: Full-page OCR via pytesseract or Azure
      - Hybrid: Text pages use standard, image pages use OCR
    """

    _ENGINES: dict[ExtractionEngine, Union[type[PDFExtractor], Callable]] = {
        ExtractionEngine.PYMUPDF: PyMuPDFExtractor,
        ExtractionEngine.PDFPLUMBER: PdfPlumberExtractor,
        ExtractionEngine.TIKA: TikaExtractor,
        ExtractionEngine.PDFMINER: PdfMinerExtractor,
        ExtractionEngine.PEGBOX: lambda: SpringBootExtractor(engine="pegbox"),
        ExtractionEngine.PDFBOX: lambda: SpringBootExtractor(engine="pdfbox"),
        # OCR — full-page OCR for all pages
        ExtractionEngine.OCR_PYTESSERACT: lambda: HybridOCRExtractor(
            ocr_engine=OCREngine.PYTESSERACT, ocr_all_pages=True
        ),
        ExtractionEngine.OCR_AZURE: lambda: HybridOCRExtractor(
            ocr_engine=OCREngine.AZURE_DOC_INTELLIGENCE, ocr_all_pages=True
        ),
        # Hybrid — OCR only for image-dominant pages, text extractor for rest
        ExtractionEngine.HYBRID_OCR_PYTESSERACT: lambda: HybridOCRExtractor(
            ocr_engine=OCREngine.PYTESSERACT, ocr_all_pages=False
        ),
        ExtractionEngine.HYBRID_OCR_AZURE: lambda: HybridOCRExtractor(
            ocr_engine=OCREngine.AZURE_DOC_INTELLIGENCE, ocr_all_pages=False
        ),
    }

    @classmethod
    def get_extractor(
        cls,
        engine: ExtractionEngine,
        *,
        page_numbers: list[int] | None = None,
        text_engine_name: str = "pdfminer",
    ) -> PDFExtractor:
        """Get extractor instance for the requested engine.

        Args:
            engine: The extraction engine to use.
            page_numbers: Optional 0-indexed page numbers for selective extraction.
                          Currently supported by PDFMINER engine.
            text_engine_name: For hybrid engines, which text extractor to pair
                             with OCR ('pdfminer', 'pymupdf', 'pdfplumber').
        """
        # Special handling for engines that accept page_numbers
        if engine == ExtractionEngine.PDFMINER:
            return PdfMinerExtractor(page_numbers=page_numbers)

        # Hybrid / OCR engines with configurable text engine
        if engine == ExtractionEngine.OCR_PYTESSERACT:
            return HybridOCRExtractor(
                ocr_engine=OCREngine.PYTESSERACT,
                ocr_all_pages=True,
                text_engine_name=text_engine_name,
            )
        if engine == ExtractionEngine.OCR_AZURE:
            return HybridOCRExtractor(
                ocr_engine=OCREngine.AZURE_DOC_INTELLIGENCE,
                ocr_all_pages=True,
                text_engine_name=text_engine_name,
            )
        if engine == ExtractionEngine.HYBRID_OCR_PYTESSERACT:
            return HybridOCRExtractor(
                ocr_engine=OCREngine.PYTESSERACT,
                ocr_all_pages=False,
                text_engine_name=text_engine_name,
            )
        if engine == ExtractionEngine.HYBRID_OCR_AZURE:
            return HybridOCRExtractor(
                ocr_engine=OCREngine.AZURE_DOC_INTELLIGENCE,
                ocr_all_pages=False,
                text_engine_name=text_engine_name,
            )

        builder = cls._ENGINES.get(engine)
        if builder is None:
            raise ValueError(f"Unsupported extraction engine: {engine}")

        # If it's a lambda/callable that returns an instance, call it.
        # If it's a class, instantiate it.
        instance = builder()
        if not isinstance(instance, PDFExtractor):
            raise TypeError(f"Engine builder did not return a PDFExtractor: {type(instance)}")
        return instance
