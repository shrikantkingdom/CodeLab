"""Enumerations for document types, extraction engines, and comparison statuses."""

from enum import Enum


class DocumentType(str, Enum):
    """Type of financial document being processed."""
    STATEMENT = "statement"
    LETTER = "letter"
    CONFIRM = "confirm"


class StatementType(str, Enum):
    """Types of account statements."""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    INTERIM = "interim"


class LetterType(str, Enum):
    """Types of correspondence letters."""
    TAX = "tax"
    REGULATORY = "regulatory"
    NOTIFICATION = "notification"
    CONFIRMATION = "confirmation"


class ConfirmType(str, Enum):
    """Types of trade/transaction confirmations."""
    TRADE = "trade"
    TRANSFER = "transfer"
    DIVIDEND = "dividend"
    CORPORATE_ACTION = "corporate_action"


class ProductType(str, Enum):
    """Product / branding categories."""
    WEALTH_MANAGEMENT = "wealth_management"
    RETAIL = "retail"
    INSTITUTIONAL = "institutional"
    PRIVATE_BANKING = "private_banking"


class ExtractionEngine(str, Enum):
    """PDF extraction engine selection."""
    PYMUPDF = "pymupdf"
    PDFPLUMBER = "pdfplumber"
    TIKA = "tika"
    PEGBOX = "pegbox"       # Java / Spring Boot
    PDFBOX = "pdfbox"       # Java / Spring Boot fallback
    OCR_PYTESSERACT = "ocr_pytesseract"         # Full OCR via pytesseract
    OCR_AZURE = "ocr_azure"                     # Full OCR via Azure Doc Intelligence
    PDFMINER = "pdfminer"     # pdfminer.six — layout-aware extraction with page selection
    HYBRID_OCR_PYTESSERACT = "hybrid_pytesseract"  # Hybrid: text pages + OCR image pages
    HYBRID_OCR_AZURE = "hybrid_azure"              # Hybrid: text pages + Azure OCR image pages


class ComparisonStatus(str, Enum):
    """Result status for individual field comparisons."""
    MATCH = "match"
    MISMATCH = "mismatch"
    MISSING_IN_PDF = "missing_in_pdf"
    MISSING_IN_DB = "missing_in_db"
    NOT_COMPARED = "not_compared"
