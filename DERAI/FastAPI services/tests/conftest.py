"""Shared test fixtures for DERAI FastAPI tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Minimal valid PDF bytes for testing."""
    # Minimal PDF 1.0 structure
    return (
        b"%PDF-1.0\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )


@pytest.fixture
def sample_extraction_result() -> dict:
    """Sample AI-classified extraction result."""
    return {
        "account_number": "001-000123",
        "statement_date": "2026-03-01",
        "period_start": "2026-03-01",
        "period_end": "2026-03-31",
        "account_name": "John Doe",
        "account_type": "Investment",
        "beginning_balance": 50000.00,
        "ending_balance": 52350.75,
        "total_deposits": 5000.00,
        "total_withdrawals": 2649.25,
        "product": "wealth_management",
        "branding": "Premium",
    }


@pytest.fixture
def sample_db_record() -> dict:
    """Sample database record matching the extraction result."""
    return {
        "account_number": "001-000123",
        "statement_date": "2026-03-01",
        "period_start": "2026-03-01",
        "period_end": "2026-03-31",
        "account_name": "John Doe",
        "account_type": "Investment",
        "beginning_balance": 50000.00,
        "ending_balance": 52350.75,
        "total_deposits": 5000.00,
        "total_withdrawals": 2649.25,
        "product": "wealth_management",
        "branding": "Premium",
    }


@pytest.fixture
def api_key_headers() -> dict[str, str]:
    """Headers with valid API key."""
    return {"X-API-Key": "dev-api-key-change-me"}


@pytest.fixture
async def async_client(api_key_headers):
    """Async test client for FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=api_key_headers) as client:
        yield client
