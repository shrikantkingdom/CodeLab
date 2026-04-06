"""Abstract base class for OCR extraction engines."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class OCREngine(str, Enum):
    """OCR engine selection."""
    PYTESSERACT = "pytesseract"
    AZURE_DOC_INTELLIGENCE = "azure_doc_intelligence"
    AWS_TEXTRACT = "aws_textract"
    GCP_VISION = "gcp_vision"


class OCRExtractor(ABC):
    """Base interface for OCR-based text extraction from images.

    Implement this class to add a new OCR provider (cloud or local).
    """

    @abstractmethod
    async def extract_from_image(self, image_bytes: bytes) -> dict[str, Any]:
        """Extract text from a single image.

        Args:
            image_bytes: Raw image bytes (PNG/JPEG).

        Returns:
            Dictionary with keys:
                - text (str): Extracted text from the image.
                - confidence (float): 0.0–1.0 extraction confidence.
                - metadata (dict): Engine-specific metadata.
        """
        ...

    @abstractmethod
    async def extract_from_images_batch(self, images: list[bytes]) -> list[dict[str, Any]]:
        """Extract text from multiple images (batch).

        Args:
            images: List of raw image bytes.

        Returns:
            List of extraction results, one per image.
        """
        ...

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Return the OCR engine identifier."""
        ...
