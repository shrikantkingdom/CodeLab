"""Service for downloading PDF documents from external APIs (mocked initially)."""

import logging
import asyncio
from typing import Any

import httpx

from app.config import settings
from app.models.enums import DocumentType
from app.models.request_models import AccountNumber

logger = logging.getLogger(__name__)


class PdfDownloadService:
    """Downloads PDF documents from an external document management API."""

    def __init__(self) -> None:
        self.base_url = settings.pdf_api_base_url
        self.timeout = settings.pdf_api_timeout

    async def download(
        self,
        account: AccountNumber,
        document_type: DocumentType,
        params: dict[str, Any],
    ) -> bytes:
        """Download a single PDF document.

        Args:
            account: The account number (office + account).
            document_type: Type of document (statement/letter/confirm).
            params: Additional query params (dates, types, product, etc.).

        Returns:
            Raw PDF bytes.

        Raises:
            httpx.HTTPStatusError: If the external API returns an error.
        """
        endpoint = f"{self.base_url}/documents/{document_type.value}"
        query = {
            "office": account.office,
            "account": account.account,
            **params,
        }

        logger.info(
            "Downloading PDF",
            extra={"account": account.full_account, "doc_type": document_type.value},
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(endpoint, params=query)
            response.raise_for_status()
            return response.content

    async def download_batch(
        self,
        requests: list[dict[str, Any]],
    ) -> list[tuple[str, bytes | None, str | None]]:
        """Download multiple PDFs concurrently.

        Args:
            requests: List of dicts with keys: account, document_type, params.

        Returns:
            List of (account_number, pdf_bytes_or_None, error_or_None).
        """
        tasks = [
            self._safe_download(req["account"], req["document_type"], req["params"])
            for req in requests
        ]
        return await asyncio.gather(*tasks)

    async def _safe_download(
        self,
        account: AccountNumber,
        document_type: DocumentType,
        params: dict[str, Any],
    ) -> tuple[str, bytes | None, str | None]:
        """Download with error capture (never raises)."""
        try:
            pdf_bytes = await self.download(account, document_type, params)
            return account.full_account, pdf_bytes, None
        except Exception as e:
            logger.error(
                "PDF download failed",
                extra={"account": account.full_account, "error": str(e)},
            )
            return account.full_account, None, str(e)
