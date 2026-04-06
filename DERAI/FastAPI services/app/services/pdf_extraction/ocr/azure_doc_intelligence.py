"""Azure AI Document Intelligence OCR extraction (formerly Form Recognizer).

Requires: azure-ai-documentintelligence SDK.
Install: pip install azure-ai-documentintelligence

Setup: Azure portal → Create "Document Intelligence" resource → get endpoint + key.
"""

import logging
from typing import Any

from app.services.pdf_extraction.ocr.base_ocr import OCRExtractor

logger = logging.getLogger(__name__)


class AzureDocIntelligenceExtractor(OCRExtractor):
    """Extract text from images/PDFs using Azure AI Document Intelligence."""

    def __init__(self, endpoint: str = "", api_key: str = "", model_id: str = "prebuilt-read"):
        """
        Args:
            endpoint: Azure Document Intelligence endpoint URL.
            api_key: Azure API key.
            model_id: Model to use. Options:
                - 'prebuilt-read': General OCR (best for mixed content)
                - 'prebuilt-layout': Layout/table extraction
                - 'prebuilt-document': Key-value pair extraction
                - 'prebuilt-invoice': Invoice-specific extraction
        """
        self._endpoint = endpoint
        self._api_key = api_key
        self._model_id = model_id
        self._client = None

    def _get_client(self):
        """Lazy-init the Azure client."""
        if self._client is None:
            try:
                from azure.ai.documentintelligence import DocumentIntelligenceClient
                from azure.core.credentials import AzureKeyCredential

                if not self._endpoint or not self._api_key:
                    logger.warning("Azure Document Intelligence not configured — returning mock")
                    return None

                self._client = DocumentIntelligenceClient(
                    endpoint=self._endpoint,
                    credential=AzureKeyCredential(self._api_key),
                )
            except ImportError:
                logger.error("azure-ai-documentintelligence SDK not installed")
                return None
        return self._client

    @property
    def engine_name(self) -> str:
        return "azure_doc_intelligence"

    async def extract_from_image(self, image_bytes: bytes) -> dict[str, Any]:
        """Extract text from a single image using Azure Document Intelligence."""
        client = self._get_client()

        if client is None:
            # Mock response for development without Azure credentials
            return self._mock_response()

        try:
            poller = client.begin_analyze_document(
                model_id=self._model_id,
                analyze_request=image_bytes,
                content_type="application/octet-stream",
            )
            result = poller.result()

            text_parts = []
            confidences = []

            for page in result.pages:
                for line in page.lines:
                    text_parts.append(line.content)
                for word in page.words:
                    if word.confidence is not None:
                        confidences.append(word.confidence)

            full_text = "\n".join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            return {
                "text": full_text,
                "confidence": round(avg_confidence, 4),
                "metadata": {
                    "engine": "azure_doc_intelligence",
                    "model_id": self._model_id,
                    "page_count": len(result.pages),
                    "word_count": len(full_text.split()),
                },
            }
        except Exception as e:
            logger.error("Azure extraction failed: %s", e)
            return {"text": "", "confidence": 0.0, "metadata": {"error": str(e)}}

    async def extract_from_images_batch(self, images: list[bytes]) -> list[dict[str, Any]]:
        """Process batch — Azure supports single-document per call, so we loop."""
        results = []
        for img_bytes in images:
            result = await self.extract_from_image(img_bytes)
            results.append(result)
        return results

    def _mock_response(self) -> dict[str, Any]:
        """Return mock response for development without Azure credentials."""
        return {
            "text": "[MOCK Azure OCR] Sample extracted text from document image",
            "confidence": 0.95,
            "metadata": {
                "engine": "azure_doc_intelligence",
                "model_id": self._model_id,
                "mock": True,
            },
        }
