"""Tests for Pydantic request/response models."""

import pytest
from pydantic import ValidationError

from app.models.enums import (
    ConfirmType,
    DocumentType,
    ExtractionEngine,
    LetterType,
    ProductType,
    StatementType,
)
from app.models.request_models import (
    AccountNumber,
    ConfirmInput,
    LetterInput,
    ProcessSingleRequest,
    StatementInput,
)
from app.models.response_models import ComparisonResult, FieldComparison
from app.models.enums import ComparisonStatus


class TestAccountNumber:
    def test_pad_office(self):
        acc = AccountNumber(office="1", account="123456")
        assert acc.office == "001"

    def test_pad_account(self):
        acc = AccountNumber(office="001", account="123")
        assert acc.account == "000123"

    def test_full_account(self):
        acc = AccountNumber(office="12", account="5678")
        assert acc.full_account == "012-005678"

    def test_already_padded(self):
        acc = AccountNumber(office="001", account="123456")
        assert acc.office == "001"
        assert acc.account == "123456"


class TestStatementInput:
    def test_valid_date_range(self):
        s = StatementInput(
            date_from="2026-01-01",
            date_to="2026-01-31",
            statement_type=StatementType.MONTHLY,
            product=ProductType.WEALTH_MANAGEMENT,
        )
        assert s.date_from.year == 2026

    def test_invalid_date_range(self):
        with pytest.raises(ValidationError, match="date_to must be >= date_from"):
            StatementInput(
                date_from="2026-02-01",
                date_to="2026-01-01",
                statement_type=StatementType.MONTHLY,
                product=ProductType.RETAIL,
            )


class TestProcessSingleRequest:
    def test_statement_request(self):
        req = ProcessSingleRequest(
            account=AccountNumber(office="1", account="123"),
            document_type=DocumentType.STATEMENT,
            extraction_engine=ExtractionEngine.PYMUPDF,
            statement=StatementInput(
                statement_date="2026-03-01",
                statement_type=StatementType.MONTHLY,
                product=ProductType.WEALTH_MANAGEMENT,
            ),
        )
        assert req.account.full_account == "001-000123"
        assert req.document_type == DocumentType.STATEMENT

    def test_letter_request(self):
        req = ProcessSingleRequest(
            account=AccountNumber(office="100", account="999999"),
            document_type=DocumentType.LETTER,
            letter=LetterInput(letter_type=LetterType.TAX, load_date="2026-03-15"),
        )
        assert req.letter.letter_type == LetterType.TAX


class TestFieldComparison:
    def test_match_field(self):
        fc = FieldComparison(
            field_name="account_number",
            pdf_value="001-000123",
            db_value="001-000123",
            status=ComparisonStatus.MATCH,
            confidence=1.0,
        )
        assert fc.status == ComparisonStatus.MATCH

    def test_mismatch_field(self):
        fc = FieldComparison(
            field_name="ending_balance",
            pdf_value=52350.75,
            db_value=52000.00,
            status=ComparisonStatus.MISMATCH,
            confidence=0.0,
        )
        assert fc.status == ComparisonStatus.MISMATCH
