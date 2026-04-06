"""Pytesseract OCR extraction — local, open-source OCR engine.

Requires: pytesseract, Pillow, and tesseract-ocr system binary.
Install: pip install pytesseract Pillow
System:  brew install tesseract (macOS) / apt-get install tesseract-ocr (Linux)
"""

import io
import logging
from typing import Any

from app.services.pdf_extraction.ocr.base_ocr import OCRExtractor

logger = logging.getLogger(__name__)


class PytesseractExtractor(OCRExtractor):
    """Extract text from images using Google's Tesseract OCR (via pytesseract)."""

    def __init__(self, lang: str = "eng", config: str = "--oem 3 --psm 6"):
        """
        Args:
            lang: Tesseract language code (e.g., 'eng', 'eng+fra').
            config: Tesseract config flags.
                --oem 3: Default LSTM engine
                --psm 6: Assume uniform block of text
        """
        self._lang = lang
        self._config = config

    @property
    def engine_name(self) -> str:
        return "pytesseract"

    async def extract_from_image(self, image_bytes: bytes) -> dict[str, Any]:
        """Extract text from a single image using pytesseract."""
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            logger.error("pytesseract or Pillow not installed")
            return {"text": "", "confidence": 0.0, "metadata": {"error": "pytesseract not installed"}}

        try:
            image = Image.open(io.BytesIO(image_bytes))

            # Get text
            text = pytesseract.image_to_string(image, lang=self._lang, config=self._config)

            # Get confidence via detailed data
            data = pytesseract.image_to_data(image, lang=self._lang, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data["conf"] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            return {
                "text": text.strip(),
                "confidence": round(avg_confidence, 4),
                "metadata": {
                    "engine": "pytesseract",
                    "lang": self._lang,
                    "word_count": len(text.split()),
                },
            }
        except Exception as e:
            logger.error("Pytesseract extraction failed: %s", e)
            return {"text": "", "confidence": 0.0, "metadata": {"error": str(e)}}

    async def extract_from_images_batch(self, images: list[bytes]) -> list[dict[str, Any]]:
        """Process multiple images sequentially (pytesseract is single-threaded)."""
        results = []
        for img_bytes in images:
            result = await self.extract_from_image(img_bytes)
            results.append(result)
        return results
