"""OCR extraction engines — pytesseract and Azure Document Intelligence.

These extractors handle image-heavy PDF pages where text-based extraction fails.
The HybridOCRExtractor provides page-level engine selection:
- Text pages → standard extractor (PyMuPDF, pdfplumber, etc.)
- Image pages → OCR extractor (pytesseract, Azure, AWS Textract, GCP Vision)
"""

from app.services.pdf_extraction.ocr.base_ocr import OCRExtractor, OCREngine
from app.services.pdf_extraction.ocr.pytesseract_extractor import PytesseractExtractor
from app.services.pdf_extraction.ocr.azure_doc_intelligence import AzureDocIntelligenceExtractor
from app.services.pdf_extraction.ocr.hybrid_extractor import HybridOCRExtractor

__all__ = [
    "OCRExtractor",
    "OCREngine",
    "PytesseractExtractor",
    "AzureDocIntelligenceExtractor",
    "HybridOCRExtractor",
]
