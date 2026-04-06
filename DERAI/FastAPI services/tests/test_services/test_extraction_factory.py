"""Tests for the PDF extraction factory."""

import pytest

from app.models.enums import ExtractionEngine
from app.services.pdf_extraction.base import PDFExtractor
from app.services.pdf_extraction.factory import ExtractorFactory


class TestExtractorFactory:
    @pytest.mark.parametrize(
        "engine",
        [
            ExtractionEngine.PYMUPDF,
            ExtractionEngine.PDFPLUMBER,
            ExtractionEngine.TIKA,
            ExtractionEngine.PEGBOX,
            ExtractionEngine.PDFBOX,
        ],
    )
    def test_get_extractor(self, engine):
        extractor = ExtractorFactory.get_extractor(engine)
        assert isinstance(extractor, PDFExtractor)

    def test_invalid_engine_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            ExtractorFactory.get_extractor("nonexistent")
