"""Comparison engine — compares extracted PDF data against database records."""

import logging
from typing import Any

from app.models.enums import ComparisonStatus, DocumentType
from app.models.response_models import FieldComparison

logger = logging.getLogger(__name__)

# Field mappings: maps AI-extracted keys → DB column names per document type
FIELD_MAPPINGS: dict[DocumentType, dict[str, str]] = {
    DocumentType.STATEMENT: {
        "account_number": "account_number",
        "account_name": "account_name",
        "period_start": "period_start",
        "period_end": "period_end",
        "starting_value": "starting_value",
        "ending_value": "ending_value",
        "deposits_withdrawals": "deposits_withdrawals",
        "dividends_interest": "dividends_interest",
        "change_in_value_of_investments": "change_in_value_of_investments",
        "total_ending_value": "total_ending_value",
        "total_accruals": "total_accruals",
        "cash_value": "cash_value",
        "cash_pct": "cash_pct",
        "equity_value": "equity_value",
        "equity_pct": "equity_pct",
        "fixed_income_value": "fixed_income_value",
        "fixed_income_pct": "fixed_income_pct",
        "accruals_value": "accruals_value",
        "accruals_pct": "accruals_pct",
        "realized_gain_loss_short_term_period": "realized_gain_loss_short_term_period",
        "realized_gain_loss_short_term_ytd": "realized_gain_loss_short_term_ytd",
        "realized_gain_loss_long_term_period": "realized_gain_loss_long_term_period",
        "realized_gain_loss_long_term_ytd": "realized_gain_loss_long_term_ytd",
        "product": "product",
        "branding": "branding",
    },
    DocumentType.LETTER: {
        "account_number": "account_number",
        "letter_date": "letter_date",
        "letter_type": "letter_type",
        "recipient_name": "recipient_name",
        "subject": "subject",
    },
    DocumentType.CONFIRM: {
        "account_number": "account_number",
        "confirm_date": "confirm_date",
        "trade_date": "trade_date",
        "settlement_date": "settlement_date",
        "confirm_type": "confirm_type",
        "security_name": "security_name",
        "symbol": "symbol",
        "quantity": "quantity",
        "price": "price",
        "net_amount": "net_amount",
        "product": "product",
        "branding": "branding",
    },
}


class ComparisonEngine:
    """Compares extracted PDF fields against database records."""

    def compare(
        self,
        extracted_data: dict[str, Any],
        db_record: dict[str, Any],
        document_type: DocumentType,
    ) -> list[FieldComparison]:
        """Compare extracted PDF data against DB record.

        Returns list of per-field comparison results with confidence scores.
        """
        mapping = FIELD_MAPPINGS.get(document_type, {})
        comparisons: list[FieldComparison] = []

        # Compare mapped fields
        all_keys = set(mapping.keys()) | set(db_record.keys())

        for pdf_key, db_key in mapping.items():
            pdf_val = extracted_data.get(pdf_key)
            db_val = db_record.get(db_key)

            if pdf_val is None and db_val is None:
                continue

            comparison = self._compare_field(pdf_key, pdf_val, db_val)
            comparisons.append(comparison)

        # Check for DB fields not in mapping (extra DB fields)
        mapped_db_keys = set(mapping.values())
        for db_key in db_record:
            if db_key not in mapped_db_keys:
                comparisons.append(
                    FieldComparison(
                        field_name=db_key,
                        pdf_value=None,
                        db_value=db_record[db_key],
                        status=ComparisonStatus.MISSING_IN_PDF,
                        confidence=1.0,
                        notes="DB field has no PDF mapping",
                    )
                )

        return comparisons

    def _compare_field(
        self, field_name: str, pdf_val: Any, db_val: Any
    ) -> FieldComparison:
        """Compare a single field and determine match status + confidence."""
        if pdf_val is None:
            return FieldComparison(
                field_name=field_name,
                pdf_value=pdf_val,
                db_value=db_val,
                status=ComparisonStatus.MISSING_IN_PDF,
                confidence=1.0,
            )

        if db_val is None:
            return FieldComparison(
                field_name=field_name,
                pdf_value=pdf_val,
                db_value=db_val,
                status=ComparisonStatus.MISSING_IN_DB,
                confidence=1.0,
            )

        # Normalize for comparison
        norm_pdf = self._normalize(pdf_val)
        norm_db = self._normalize(db_val)

        if norm_pdf == norm_db:
            return FieldComparison(
                field_name=field_name,
                pdf_value=pdf_val,
                db_value=db_val,
                status=ComparisonStatus.MATCH,
                confidence=1.0,
            )

        # Numeric comparison (handles int vs float, e.g. 2 vs 2.0)
        try:
            num_pdf = float(str(pdf_val))
            num_db = float(str(db_val))
            if abs(num_pdf - num_db) < 1e-6:
                return FieldComparison(
                    field_name=field_name,
                    pdf_value=pdf_val,
                    db_value=db_val,
                    status=ComparisonStatus.MATCH,
                    confidence=1.0,
                    notes="Numeric match",
                )
        except (ValueError, TypeError):
            pass

        # Fuzzy match for strings (case-insensitive, whitespace-normalized)
        if isinstance(pdf_val, str) and isinstance(db_val, str):
            confidence = self._string_similarity(norm_pdf, norm_db)
            if confidence >= 0.9:
                return FieldComparison(
                    field_name=field_name,
                    pdf_value=pdf_val,
                    db_value=db_val,
                    status=ComparisonStatus.MATCH,
                    confidence=confidence,
                    notes="Fuzzy match",
                )

        return FieldComparison(
            field_name=field_name,
            pdf_value=pdf_val,
            db_value=db_val,
            status=ComparisonStatus.MISMATCH,
            confidence=0.0,
        )

    @staticmethod
    def _normalize(value: Any) -> str:
        """Normalize a value to a lowercase stripped string for comparison."""
        return str(value).strip().lower()

    @staticmethod
    def _string_similarity(a: str, b: str) -> float:
        """Simple character-level similarity ratio (Jaccard on character bigrams)."""
        if not a or not b:
            return 0.0
        bigrams_a = {a[i : i + 2] for i in range(len(a) - 1)}
        bigrams_b = {b[i : i + 2] for i in range(len(b) - 1)}
        if not bigrams_a or not bigrams_b:
            return 1.0 if a == b else 0.0
        intersection = bigrams_a & bigrams_b
        union = bigrams_a | bigrams_b
        return len(intersection) / len(union) if union else 0.0
