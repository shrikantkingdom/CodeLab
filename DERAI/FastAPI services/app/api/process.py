"""Processing endpoints — /process-single, /process-batch, /upload-and-process."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.models.enums import DocumentType, ExtractionEngine
from app.models.request_models import AccountNumber, ProcessBatchRequest, ProcessSingleRequest
from app.models.response_models import ComparisonResult
from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Processing"])

orchestrator = Orchestrator()


@router.post("/process-single", response_model=ComparisonResult)
async def process_single(request: ProcessSingleRequest) -> ComparisonResult:
    """Process a single account document through the full pipeline.

    Pipeline: Download PDF → Extract → AI Classify → DB Fetch → Compare
    """
    return await orchestrator.process_single(request)


@router.post("/upload-and-process", response_model=ComparisonResult)
async def upload_and_process(
    file: UploadFile = File(..., description="PDF file to process"),
    office: str = Form(..., description="3-digit office code"),
    account: str = Form(..., description="6-digit account number"),
    document_type: DocumentType = Form(..., description="Document type"),
    extraction_engine: ExtractionEngine = Form(
        ExtractionEngine.PDFMINER, description="Extraction engine"
    ),
    page_numbers: Optional[str] = Form(
        None, description="Comma-separated 1-based page numbers (e.g. '1,2,3')"
    ),
    hybrid_text_engine: Optional[str] = Form(
        None,
        description="Text extractor for non-image pages in hybrid mode (pdfminer, pymupdf, pdfplumber)",
    ),
    ai_provider: Optional[str] = Form(
        None,
        description="AI provider override: openai, github_copilot, anthropic, google_gemini, deepseek, regex_only",
    ),
    ai_model: Optional[str] = Form(
        None,
        description="AI model override — e.g. gpt-4o-mini, claude-3-5-haiku-20241022, gemini-2.0-flash",
    ),
    ai_model: Optional[str] = Form(
        None,
        description="AI model override — e.g. gpt-4o-mini, claude-3-5-haiku-20241022, gemini-2.0-flash",
    ),
) -> ComparisonResult:
    """Upload a local PDF and process it through the full pipeline.

    Pipeline: Upload PDF → Extract (with page selection) → AI Classify → DB Fetch → Compare

    page_numbers: optional comma-separated 1-based page numbers.
    If omitted, all pages are extracted.
    """
    # Validate file type
    if file.content_type and file.content_type != "application/pdf":
        if not (file.filename and file.filename.lower().endswith(".pdf")):
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pdf_bytes = await file.read()
    logger.info(
        "Upload received: filename=%s, content_type=%s, size=%d bytes",
        file.filename,
        file.content_type,
        len(pdf_bytes),
    )

    # Parse page numbers (convert from 1-based user input to 0-based internal)
    parsed_pages: Optional[list[int]] = None
    if page_numbers:
        try:
            parsed_pages = [int(p.strip()) - 1 for p in page_numbers.split(",") if p.strip()]
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400, detail="page_numbers must be comma-separated integers"
            )

    account_number = AccountNumber(office=office, account=account)

    return await orchestrator.process_uploaded(
        pdf_bytes=pdf_bytes,
        account=account_number,
        document_type=document_type,
        extraction_engine=extraction_engine,
        page_numbers=parsed_pages,
        hybrid_text_engine=hybrid_text_engine,
        ai_provider=ai_provider,
        ai_model=ai_model,
    )


@router.post("/process-batch", response_model=list[ComparisonResult])
async def process_batch(request: ProcessBatchRequest) -> list[ComparisonResult]:
    """Process a batch of account documents concurrently.

    Accepts up to 500 requests. Each is processed through the full pipeline.
    The batch-level extraction_engine overrides individual request engines.
    """
    # Apply batch-level engine override
    for req in request.requests:
        req.extraction_engine = request.extraction_engine
    return await orchestrator.process_batch(request.requests)
