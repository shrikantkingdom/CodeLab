"""Pydantic response models for API output."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.models.enums import ComparisonStatus, DocumentType, ExtractionEngine


class FieldComparison(BaseModel):
    """Comparison result for a single field."""

    field_name: str
    pdf_value: Optional[Any] = None
    db_value: Optional[Any] = None
    status: ComparisonStatus
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")
    notes: Optional[str] = None


class ExtractionResult(BaseModel):
    """Result from PDF content extraction."""

    engine_used: ExtractionEngine
    raw_text: str
    structured_data: dict[str, Any] = Field(default_factory=dict)
    page_count: int = 0
    extraction_time_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None


# --- Pipeline debug models ---

class StepTiming(BaseModel):
    """Timing info for a single pipeline step."""
    step_name: str
    duration_ms: float = 0.0
    status: str = "completed"  # completed | skipped | failed


class PageDetail(BaseModel):
    """Extraction detail for a single page."""
    page_number: int  # 1-based
    method: str  # "ocr" | "text"
    engine: str  # "pytesseract", "pdfminer", etc.
    is_image_dominant: bool = False
    image_count: int = 0
    image_coverage_pct: float = 0.0
    text_chars: int = 0
    text_density: float = 0.0
    confidence: float = 1.0
    extracted_text: str = ""  # per-page text
    detection_reason: str = ""  # "image_dominant", "low_text_density", "force_all", "text_page"


class AIModelInfo(BaseModel):
    """Details about the AI model call."""
    model_config = {"protected_namespaces": ()}

    model_name: str = ""
    provider: str = ""  # openai, github_copilot, anthropic, google_gemini, regex_only
    provider_display: str = ""  # Human-readable provider name
    temperature: float = 0.0
    max_tokens: int = 0
    total_prompt_chars: int = 0
    text_chunk_sent_chars: int = 0  # actual text chunk size sent to AI
    text_chunk_max_chars: int = 8000  # max chunk size allowed
    prompt_template_chars: int = 0
    method_used: str = ""  # "openai_api" | "github_copilot_api" | "anthropic_api" | "google_gemini_api" | "regex_fallback" | "regex_only"
    ai_request_prompt: str = ""  # full prompt sent
    ai_response_raw: str = ""  # raw AI response
    response_parse_success: bool = True
    error_message: Optional[str] = None  # user-friendly error (429 quota, auth, etc.)


class DataCategory(BaseModel):
    """A logical group of fields within the classified output."""
    category_name: str
    fields: dict[str, Any] = Field(default_factory=dict)


class DebugInfo(BaseModel):
    """Comprehensive pipeline debug details."""

    # --- Timing ---
    total_processing_ms: float = 0.0
    step_timings: list[StepTiming] = Field(default_factory=list)

    # --- Extraction ---
    extraction_engine_used: Optional[str] = None
    extraction_text_engine: Optional[str] = None  # text engine in hybrid mode
    extraction_page_count: int = 0
    extraction_text_length: int = 0
    ocr_fallback_used: bool = False
    parallel_execution: bool = False

    # --- Page-level details ---
    page_details: list[PageDetail] = Field(default_factory=list)
    ocr_pages_count: int = 0
    text_pages_count: int = 0

    # --- Raw extracted text ---
    extracted_text: str = ""

    # --- AI Model ---
    ai_model_info: Optional[AIModelInfo] = None

    # --- Data segregation (pre-classification) ---
    data_categories: list[DataCategory] = Field(default_factory=list)

    # --- Classified output ---
    classified_output: dict[str, Any] = Field(default_factory=dict)

    # --- Legacy compat ---
    ai_prompt: str = ""


class ComparisonResult(BaseModel):
    """Full comparison result between extracted PDF data and database records."""

    account_number: str
    document_type: DocumentType
    extraction_engine: ExtractionEngine
    field_comparisons: list[FieldComparison] = Field(default_factory=list)
    overall_match: bool = False
    match_count: int = 0
    mismatch_count: int = 0
    missing_count: int = 0
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0
    error: Optional[str] = None
    debug_info: Optional[DebugInfo] = None


class ProcessingStatus(BaseModel):
    """Status of a batch processing job."""

    job_id: str
    total: int
    completed: int = 0
    failed: int = 0
    in_progress: int = 0
    status: str = "queued"  # queued | processing | completed | failed
    results: list[ComparisonResult] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "healthy"
    version: str = "1.0.0"
    services: dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
