"""Orchestrator — coordinates the full document processing pipeline.

Pipeline: Download PDF → Extract → AI Classify → DB Fetch → Compare
Upload:  Upload PDF → Extract (page selection) → AI Classify → DB Fetch → Compare
"""

import asyncio
import logging
import time
from typing import Any, Optional

from app.db.factory import DBFactory
from app.models.enums import ComparisonStatus, DocumentType, ExtractionEngine
from app.models.request_models import (
    AccountNumber,
    ConfirmInput,
    LetterInput,
    ProcessSingleRequest,
    StatementInput,
)
from app.models.response_models import (
    ComparisonResult, DebugInfo, ExtractionResult,
    StepTiming, PageDetail, AIModelInfo, DataCategory,
)
from app.services.ai_classification_service import AIClassificationService
from app.services.comparison_engine import ComparisonEngine
from app.services.pdf_download_service import PdfDownloadService
from app.services.pdf_extraction.factory import ExtractorFactory

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the full processing pipeline for document comparison."""

    def __init__(self) -> None:
        self.pdf_downloader = PdfDownloadService()
        self.ai_service = AIClassificationService()
        self.comparison_engine = ComparisonEngine()

    async def process_single(self, request: ProcessSingleRequest) -> ComparisonResult:
        """Process a single account document through the full pipeline."""
        start = time.time()
        account = request.account
        doc_type = request.document_type
        engine = request.extraction_engine

        try:
            # Step 1: Build download params from the document-type-specific input
            download_params = self._build_download_params(request)

            # Step 2: Download PDF
            logger.info("Downloading PDF for %s", account.full_account)
            pdf_bytes = await self.pdf_downloader.download(account, doc_type, download_params)

            # Step 3: Extract PDF content
            logger.info("Extracting with engine=%s", engine.value)
            extractor = ExtractorFactory.get_extractor(engine)
            extraction_raw = await extractor.extract(pdf_bytes)

            # Step 4: AI classification of extracted text
            logger.info("AI classifying document")
            structured_data = await self.ai_service.classify(
                extraction_raw["raw_text"], doc_type
            )

            # Step 5: Fetch database record
            logger.info("Fetching DB record")
            db_connector = DBFactory.get_connector(doc_type)
            db_record = await db_connector.fetch_record(
                account.office, account.account, download_params
            )

            # Step 6: Compare extracted vs DB
            logger.info("Comparing extracted data with DB record")
            field_comparisons = self.comparison_engine.compare(
                structured_data, db_record, doc_type
            )

            # Aggregate stats
            match_count = sum(1 for f in field_comparisons if f.status == ComparisonStatus.MATCH)
            mismatch_count = sum(1 for f in field_comparisons if f.status == ComparisonStatus.MISMATCH)
            missing_count = sum(
                1 for f in field_comparisons
                if f.status in (ComparisonStatus.MISSING_IN_PDF, ComparisonStatus.MISSING_IN_DB)
            )
            total = len(field_comparisons) or 1
            confidence = match_count / total

            elapsed_ms = (time.time() - start) * 1000

            return ComparisonResult(
                account_number=account.full_account,
                document_type=doc_type,
                extraction_engine=engine,
                field_comparisons=field_comparisons,
                overall_match=(mismatch_count == 0 and missing_count == 0),
                match_count=match_count,
                mismatch_count=mismatch_count,
                missing_count=missing_count,
                confidence_score=round(confidence, 4),
                processing_time_ms=round(elapsed_ms, 2),
            )

        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            logger.error("Processing failed for %s: %s", account.full_account, e)
            return ComparisonResult(
                account_number=account.full_account,
                document_type=doc_type,
                extraction_engine=engine,
                processing_time_ms=round(elapsed_ms, 2),
                error=str(e),
            )

    async def process_uploaded(
        self,
        pdf_bytes: bytes,
        account: AccountNumber,
        document_type: DocumentType,
        extraction_engine: ExtractionEngine,
        page_numbers: Optional[list[int]] = None,
        hybrid_text_engine: Optional[str] = None,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
    ) -> ComparisonResult:
        """Process an uploaded PDF through the full pipeline (skip download step).

        Captures detailed per-step timing, page-level extraction details,
        AI model request/response, and data segregation for full observability.
        """
        pipeline_start = time.time()
        step_timings: list[StepTiming] = []
        ocr_fallback_used = False
        text_engine = hybrid_text_engine or "pdfminer"
        engine_used = extraction_engine.value

        try:
            # ── Step 1: Extract PDF content ──
            t0 = time.time()
            logger.info("Extracting uploaded PDF with engine=%s", extraction_engine.value)
            extractor = ExtractorFactory.get_extractor(
                extraction_engine, page_numbers=page_numbers, text_engine_name=text_engine,
            )
            extraction_raw = await extractor.extract(pdf_bytes)
            raw_text = extraction_raw["raw_text"]
            page_count = extraction_raw.get("page_count", 0)
            ocr_metadata = extraction_raw.get("ocr_metadata", {})
            extraction_ms = (time.time() - t0) * 1000
            step_timings.append(StepTiming(
                step_name="PDF Extraction", duration_ms=round(extraction_ms, 2), status="completed",
            ))

            logger.info(
                "Initial extraction: engine=%s, text_len=%d, pages=%d",
                extraction_engine.value, len(raw_text), page_count,
            )

            # ── Step 1b: Auto-fallback to hybrid OCR if too little text ──
            MIN_TEXT_LENGTH = 100
            if len(raw_text.strip()) < MIN_TEXT_LENGTH:
                t0_fb = time.time()
                logger.warning(
                    "Text too short (%d chars < %d). Auto-falling back to HYBRID_OCR_PYTESSERACT.",
                    len(raw_text.strip()), MIN_TEXT_LENGTH,
                )
                ocr_fallback_used = True
                engine_used = "hybrid_ocr_pytesseract"
                ocr_extractor = ExtractorFactory.get_extractor(
                    ExtractionEngine.HYBRID_OCR_PYTESSERACT,
                    text_engine_name=text_engine,
                )
                extraction_raw = await ocr_extractor.extract(pdf_bytes)
                raw_text = extraction_raw["raw_text"]
                page_count = extraction_raw.get("page_count", 0)
                ocr_metadata = extraction_raw.get("ocr_metadata", {})
                fallback_ms = (time.time() - t0_fb) * 1000
                step_timings.append(StepTiming(
                    step_name="OCR Fallback Re-extraction",
                    duration_ms=round(fallback_ms, 2), status="completed",
                ))

            # ── Build page details from extraction metadata ──
            page_details: list[PageDetail] = []
            for pd in ocr_metadata.get("page_details", []):
                page_details.append(PageDetail(
                    page_number=pd.get("page", 0),
                    method=pd.get("method", "unknown"),
                    engine=pd.get("engine", "unknown"),
                    is_image_dominant=pd.get("is_image_dominant", False),
                    image_count=pd.get("image_count", 0),
                    image_coverage_pct=pd.get("image_coverage_pct", 0.0),
                    text_chars=pd.get("raw_text_chars", pd.get("text_length", 0)),
                    text_density=pd.get("text_density", 0.0),
                    confidence=pd.get("confidence", 1.0),
                    extracted_text=pd.get("extracted_text", ""),
                    detection_reason=pd.get("detection_reason", ""),
                ))

            # ── Step 2: AI Classification ──
            t1 = time.time()
            logger.info(
                "AI classifying uploaded document (text_len=%d)", len(raw_text),
            )
            classify_result = await self.ai_service.classify(raw_text, document_type, ai_provider=ai_provider, ai_model=ai_model)

            # classify now returns (structured_data, ai_details)
            if isinstance(classify_result, tuple):
                structured_data, ai_details = classify_result
            else:
                structured_data = classify_result
                ai_details = {}

            # ── Flatten nested AI output ──
            # AI may return {'Account Information': {'account_number': ...}, 'Asset Composition': {...}}
            # Comparison engine and segregation logic expect flat keys: {'account_number': ..., 'cash_value': ...}
            classified_output_raw = structured_data  # preserve nested form for debug
            flat_data: dict[str, Any] = {}
            for key, value in structured_data.items():
                if isinstance(value, dict):
                    flat_data.update(value)
                else:
                    flat_data[key] = value
            structured_data = flat_data

            classify_ms = (time.time() - t1) * 1000
            step_timings.append(StepTiming(
                step_name="AI Classification", duration_ms=round(classify_ms, 2), status="completed",
            ))
            logger.info(
                "Classification returned %d keys: %s",
                len(structured_data), list(structured_data.keys()),
            )

            # ── Build AI model info ──
            ai_model_info = AIModelInfo(
                model_name=ai_details.get("model_name", ""),
                provider=ai_details.get("provider", ""),
                provider_display=ai_details.get("provider_display", ""),
                temperature=ai_details.get("temperature", 0.0),
                max_tokens=ai_details.get("max_tokens", 0),
                total_prompt_chars=ai_details.get("total_prompt_chars", 0),
                text_chunk_sent_chars=ai_details.get("text_chunk_sent_chars", 0),
                text_chunk_max_chars=ai_details.get("text_chunk_max_chars", 8000),
                prompt_template_chars=ai_details.get("prompt_template_chars", 0),
                method_used=ai_details.get("method_used", ""),
                ai_request_prompt=ai_details.get("ai_request_prompt", ""),
                ai_response_raw=ai_details.get("ai_response_raw", ""),
                response_parse_success=ai_details.get("response_parse_success", True),
                error_message=ai_details.get("error_message"),
            )

            # ── Segregate classified data into categories ──
            data_categories = self._segregate_data(structured_data, document_type)

            # ── Step 3: Fetch DB record ──
            t2 = time.time()
            logger.info("Fetching DB record for comparison")
            db_connector = DBFactory.get_connector(document_type)
            download_params = {
                "document_type": document_type.value,
                "date_from": structured_data.get("period_start"),
                "date_to": structured_data.get("period_end"),
                "product": structured_data.get("product", "wealth_management"),
            }
            db_record = await db_connector.fetch_record(
                account.office, account.account, download_params
            )
            db_ms = (time.time() - t2) * 1000
            step_timings.append(StepTiming(
                step_name="Database Fetch", duration_ms=round(db_ms, 2), status="completed",
            ))

            # ── Step 4: Compare ──
            t3 = time.time()
            logger.info("Comparing extracted data with DB record")
            field_comparisons = self.comparison_engine.compare(
                structured_data, db_record, document_type
            )
            compare_ms = (time.time() - t3) * 1000
            step_timings.append(StepTiming(
                step_name="Field Comparison", duration_ms=round(compare_ms, 2), status="completed",
            ))

            # ── Aggregate stats ──
            match_count = sum(1 for f in field_comparisons if f.status == ComparisonStatus.MATCH)
            mismatch_count = sum(
                1 for f in field_comparisons if f.status == ComparisonStatus.MISMATCH
            )
            missing_count = sum(
                1
                for f in field_comparisons
                if f.status
                in (ComparisonStatus.MISSING_IN_PDF, ComparisonStatus.MISSING_IN_DB)
            )
            total = len(field_comparisons) or 1
            confidence = match_count / total
            total_ms = (time.time() - pipeline_start) * 1000

            # ── Build comprehensive debug info ──
            debug_info = DebugInfo(
                total_processing_ms=round(total_ms, 2),
                step_timings=step_timings,
                extraction_engine_used=engine_used,
                extraction_text_engine=text_engine,
                extraction_page_count=page_count,
                extraction_text_length=len(raw_text),
                ocr_fallback_used=ocr_fallback_used,
                parallel_execution=False,
                page_details=page_details,
                ocr_pages_count=ocr_metadata.get("ocr_pages", 0),
                text_pages_count=ocr_metadata.get("text_pages", 0),
                extracted_text=raw_text,
                ai_model_info=ai_model_info,
                data_categories=data_categories,
                classified_output=classified_output_raw,
                ai_prompt=ai_details.get("ai_request_prompt", ""),
            )

            return ComparisonResult(
                account_number=account.full_account,
                document_type=document_type,
                extraction_engine=extraction_engine,
                field_comparisons=field_comparisons,
                overall_match=(mismatch_count == 0 and missing_count == 0),
                match_count=match_count,
                mismatch_count=mismatch_count,
                missing_count=missing_count,
                confidence_score=round(confidence, 4),
                processing_time_ms=round(total_ms, 2),
                debug_info=debug_info,
            )

        except Exception as e:
            elapsed_ms = (time.time() - pipeline_start) * 1000
            logger.error("Upload processing failed for %s: %s", account.full_account, e)
            return ComparisonResult(
                account_number=account.full_account,
                document_type=document_type,
                extraction_engine=extraction_engine,
                processing_time_ms=round(elapsed_ms, 2),
                error=str(e),
            )

    @staticmethod
    def _segregate_data(
        classified: dict[str, Any], doc_type: DocumentType
    ) -> list[DataCategory]:
        """Segregate classified output into logical categories for display."""
        if doc_type == DocumentType.STATEMENT:
            categories_map = {
                "Account Information": [
                    "account_number", "account_name", "period_start", "period_end",
                    "product", "branding",
                ],
                "Account Summary": [
                    "starting_value", "ending_value", "deposits_withdrawals",
                    "dividends_interest", "change_in_value_of_investments",
                    "total_ending_value", "total_accruals",
                ],
                "Asset Composition": [
                    "cash_value", "cash_pct", "equity_value", "equity_pct",
                    "fixed_income_value", "fixed_income_pct",
                    "accruals_value", "accruals_pct",
                ],
                "Realized Gain/Loss": [
                    "realized_gain_loss_short_term_period",
                    "realized_gain_loss_short_term_ytd",
                    "realized_gain_loss_long_term_period",
                    "realized_gain_loss_long_term_ytd",
                ],
            }
        elif doc_type == DocumentType.LETTER:
            categories_map = {
                "Letter Details": [
                    "account_number", "letter_date", "letter_type",
                    "recipient_name", "subject",
                ],
                "Key Details": ["key_details"],
            }
        elif doc_type == DocumentType.CONFIRM:
            categories_map = {
                "Trade Details": [
                    "account_number", "confirm_date", "trade_date",
                    "settlement_date", "confirm_type",
                ],
                "Security Info": [
                    "security_name", "symbol", "quantity", "price", "net_amount",
                ],
                "Metadata": ["product", "branding"],
            }
        else:
            categories_map = {"All Fields": list(classified.keys())}

        result: list[DataCategory] = []
        categorized_keys: set[str] = set()

        for cat_name, fields in categories_map.items():
            cat_fields = {}
            for f in fields:
                if f in classified:
                    cat_fields[f] = classified[f]
                    categorized_keys.add(f)
            if cat_fields:
                result.append(DataCategory(category_name=cat_name, fields=cat_fields))

        # Catch un-categorized fields
        remaining = {k: v for k, v in classified.items() if k not in categorized_keys}
        if remaining:
            result.append(DataCategory(category_name="Other Fields", fields=remaining))

        return result

    async def process_batch(
        self, requests: list[ProcessSingleRequest]
    ) -> list[ComparisonResult]:
        """Process multiple accounts concurrently."""
        tasks = [self.process_single(req) for req in requests]
        return await asyncio.gather(*tasks)

    @staticmethod
    def _build_download_params(request: ProcessSingleRequest) -> dict[str, Any]:
        """Extract download parameters from the document-specific input."""
        params: dict[str, Any] = {"document_type": request.document_type.value}

        if request.document_type == DocumentType.STATEMENT and request.statement:
            s: StatementInput = request.statement
            params["date_from"] = str(s.date_from) if s.date_from else None
            params["date_to"] = str(s.date_to) if s.date_to else None
            params["statement_date"] = str(s.statement_date) if s.statement_date else None
            params["statement_type"] = s.statement_type.value
            params["product"] = s.product.value

        elif request.document_type == DocumentType.LETTER and request.letter:
            lt: LetterInput = request.letter
            params["letter_type"] = lt.letter_type.value
            params["load_date"] = str(lt.load_date)

        elif request.document_type == DocumentType.CONFIRM and request.confirm:
            c: ConfirmInput = request.confirm
            params["date_from"] = str(c.date_from) if c.date_from else None
            params["date_to"] = str(c.date_to) if c.date_to else None
            params["confirm_date"] = str(c.confirm_date) if c.confirm_date else None
            params["confirm_type"] = c.confirm_type.value
            params["product"] = c.product.value

        return params
