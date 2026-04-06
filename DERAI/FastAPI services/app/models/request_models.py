"""Pydantic request models for API input validation."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import (
    ConfirmType,
    DocumentType,
    ExtractionEngine,
    LetterType,
    ProductType,
    StatementType,
)


class AccountNumber(BaseModel):
    """Account identifier with office and account number, auto-padded."""

    office: str = Field(..., description="3-digit office code (auto-padded with leading zeros)")
    account: str = Field(..., description="6-digit account number (auto-padded with leading zeros)")

    @field_validator("office")
    @classmethod
    def pad_office(cls, v: str) -> str:
        return v.strip().zfill(3)

    @field_validator("account")
    @classmethod
    def pad_account(cls, v: str) -> str:
        return v.strip().zfill(6)

    @property
    def full_account(self) -> str:
        return f"{self.office}-{self.account}"


class StatementInput(BaseModel):
    """Input parameters for statement document processing."""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    statement_date: Optional[date] = None
    statement_type: StatementType
    product: ProductType

    @field_validator("date_to")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        date_from = info.data.get("date_from")
        if v and date_from and v < date_from:
            raise ValueError("date_to must be >= date_from")
        return v


class LetterInput(BaseModel):
    """Input parameters for letter document processing."""

    letter_type: LetterType
    load_date: date


class ConfirmInput(BaseModel):
    """Input parameters for confirmation document processing."""

    date_from: Optional[date] = None
    date_to: Optional[date] = None
    confirm_date: Optional[date] = None
    confirm_type: ConfirmType
    product: ProductType

    @field_validator("date_to")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        date_from = info.data.get("date_from")
        if v and date_from and v < date_from:
            raise ValueError("date_to must be >= date_from")
        return v


class ProcessSingleRequest(BaseModel):
    """Request body for /process-single endpoint."""

    account: AccountNumber
    document_type: DocumentType
    extraction_engine: ExtractionEngine = ExtractionEngine.PYMUPDF

    # Only one of these should be set based on document_type
    statement: Optional[StatementInput] = None
    letter: Optional[LetterInput] = None
    confirm: Optional[ConfirmInput] = None

    @field_validator("statement", "letter", "confirm")
    @classmethod
    def check_document_input(cls, v, info):
        """Validation happens at the API layer — at least one doc input must match type."""
        return v


class ProcessBatchRequest(BaseModel):
    """Request body for /process-batch endpoint."""

    requests: list[ProcessSingleRequest] = Field(
        ..., min_length=1, max_length=500, description="Batch of processing requests"
    )
    extraction_engine: ExtractionEngine = ExtractionEngine.PYMUPDF
