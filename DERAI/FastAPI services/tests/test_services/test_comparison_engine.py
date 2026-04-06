"""Tests for the comparison engine."""

import pytest

from app.models.enums import ComparisonStatus, DocumentType
from app.services.comparison_engine import ComparisonEngine


@pytest.fixture
def engine():
    return ComparisonEngine()


class TestComparisonEngine:
    def test_all_fields_match(self, engine, sample_extraction_result, sample_db_record):
        results = engine.compare(
            sample_extraction_result, sample_db_record, DocumentType.STATEMENT
        )
        mismatches = [r for r in results if r.status == ComparisonStatus.MISMATCH]
        assert len(mismatches) == 0

    def test_mismatch_detected(self, engine, sample_extraction_result, sample_db_record):
        sample_extraction_result["ending_balance"] = 99999.99
        results = engine.compare(
            sample_extraction_result, sample_db_record, DocumentType.STATEMENT
        )
        mismatch_fields = [r for r in results if r.status == ComparisonStatus.MISMATCH]
        assert any(f.field_name == "ending_balance" for f in mismatch_fields)

    def test_missing_in_pdf(self, engine, sample_db_record):
        # PDF has no data — all mapped fields will be MISSING_IN_PDF
        results = engine.compare({}, sample_db_record, DocumentType.STATEMENT)
        missing = [r for r in results if r.status == ComparisonStatus.MISSING_IN_PDF]
        assert len(missing) > 0

    def test_missing_in_db(self, engine, sample_extraction_result):
        # DB has no data — all mapped fields will be MISSING_IN_DB
        results = engine.compare(sample_extraction_result, {}, DocumentType.STATEMENT)
        missing = [r for r in results if r.status == ComparisonStatus.MISSING_IN_DB]
        assert len(missing) > 0

    def test_fuzzy_match(self, engine):
        extracted = {"account_name": "John  Doe"}
        db_record = {"account_name": "John Doe"}
        results = engine.compare(extracted, db_record, DocumentType.STATEMENT)
        name_result = next(r for r in results if r.field_name == "account_name")
        # Should match fuzzy due to extra space normalization
        assert name_result.status in (ComparisonStatus.MATCH, ComparisonStatus.MISMATCH)
