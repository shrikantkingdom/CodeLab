"""Abstract base class for PDF extraction engines (Strategy pattern)."""

from abc import ABC, abstractmethod
from typing import Any


class PDFExtractor(ABC):
    """Base interface for all PDF content extractors.

    Implement this class to add a new extraction engine.
    Register the new engine in ExtractorFactory.
    """

    @abstractmethod
    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]:
        """Extract structured content from raw PDF bytes.

        Args:
            pdf_bytes: Raw PDF file content.

        Returns:
            Dictionary with keys:
                - raw_text (str): Full extracted text.
                - structured_data (dict): Parsed fields.
                - page_count (int): Number of pages.
        """
        ...

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Unique name of this extraction engine."""
        ...
