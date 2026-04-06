# FastAPI Service — In-Depth Documentation

## Overview
The FastAPI service is the **orchestrator** of the DERAI system. It coordinates the entire document processing pipeline: PDF download → extraction → AI classification → database comparison. React UI only communicates with this service.

## Project Structure
```
FastAPI services/
├── main.py                              # App entrypoint, CORS, middleware
├── app/
│   ├── config.py                        # Pydantic BaseSettings (env-driven)
│   ├── models/
│   │   ├── enums.py                     # DocumentType, ExtractionEngine, etc.
│   │   ├── request_models.py            # Input validation (AccountNumber, etc.)
│   │   └── response_models.py           # Output schemas (ComparisonResult, etc.)
│   ├── api/
│   │   ├── router.py                    # Aggregates all route modules
│   │   ├── process.py                   # /process-single, /process-batch
│   │   ├── compare.py                   # /compare-results (in-memory store)
│   │   └── health.py                    # /health (dependency checks)
│   ├── services/
│   │   ├── orchestrator.py              # Full pipeline coordinator
│   │   ├── pdf_download_service.py      # Downloads PDFs via httpx
│   │   ├── ai_classification_service.py # OpenAI GPT-4o structured extraction
│   │   ├── comparison_engine.py         # Field-by-field compare + fuzzy match
│   │   └── pdf_extraction/
│   │       ├── base.py                  # Abstract PDFExtractor (Strategy)
│   │       ├── pymupdf_extractor.py     # fitz library
│   │       ├── pdfplumber_extractor.py  # pdfplumber + table extraction
│   │       ├── tika_extractor.py        # Apache Tika
│   │       ├── springboot_extractor.py  # Delegates to Java backend
│   │       ├── factory.py               # ExtractorFactory.get_extractor()
│   │       └── ocr/
│   │           ├── base_ocr.py          # Abstract OCRExtractor
│   │           ├── pytesseract_extractor.py  # Tesseract OCR (local)
│   │           ├── azure_doc_intelligence.py # Azure AI Document Intelligence
│   │           └── hybrid_extractor.py  # Page-level OCR/text routing
│   ├── db/
│   │   ├── base.py                      # Abstract DBConnector
│   │   ├── snowflake_connector.py       # Statements (mock/real)
│   │   ├── db2_connector.py             # Letters & confirms (mock/real)
│   │   └── factory.py                   # DBFactory by document type
│   ├── middleware/
│   │   ├── auth.py                      # X-API-Key validation
│   │   └── logging_middleware.py        # Structured JSON logging
│   └── utils/
│       ├── padding.py                   # Office/account auto-padding
│       └── date_utils.py               # Date range helpers
├── tests/
│   ├── conftest.py                      # Shared fixtures
│   ├── test_api/test_endpoints.py
│   ├── test_models/test_models.py
│   └── test_services/
│       ├── test_comparison_engine.py
│       └── test_extraction_factory.py
├── requirements.txt
├── Dockerfile
└── pyproject.toml
```

## Key Implementation Details

### 1. Strategy Pattern — PDF Extraction
Each extraction engine implements the `PDFExtractor` abstract base class:
```python
class PDFExtractor(ABC):
    async def extract(self, pdf_bytes: bytes) -> dict[str, Any]: ...
    def engine_name(self) -> str: ...
```

The `ExtractorFactory` maps `ExtractionEngine` enum → concrete class. Adding a new engine requires:
1. Create a class implementing `PDFExtractor`
2. Register it in `ExtractorFactory._ENGINES`

### 2. Hybrid OCR Architecture
The `HybridOCRExtractor` provides page-level intelligence:
- Opens PDF with PyMuPDF, iterates each page
- Classifies page as text-dominant or image-dominant using heuristic:
  - Text length < 50 chars + has images → image page
  - Text density (chars/area) below threshold → image page
- Text pages: extracted directly by PyMuPDF (fast, accurate)
- Image pages: rendered to 300 DPI PNG → sent to OCR engine
- All page texts merged in order → single unified output

### 3. AI Classification
- Per-document-type prompt templates define exact JSON fields to extract
- OpenAI `response_format={"type": "json_object"}` ensures valid JSON
- Fallback to regex-based extraction if OpenAI key not set or API fails

### 4. Comparison Engine
- `FIELD_MAPPINGS` dict defines PDF key → DB key mappings per document type
- Exact string match first, then fuzzy match using bigram Jaccard similarity
- Threshold: 0.9 for fuzzy match acceptance
- Returns per-field: status (match/mismatch/missing), confidence (0-1)

### 5. Mock-First Strategy
All external dependencies mock when credentials are empty:
- **Snowflake**: Mock returns realistic financial data
- **DB2**: Mock returns letter/confirm data
- **External PDF API**: Mock returns sample PDF bytes
- **OpenAI**: Falls back to regex extraction

This allows full local development without any external accounts.

## API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/v1/process-single | Process one document | Required |
| POST | /api/v1/process-batch | Process up to 500 documents | Required |
| GET | /api/v1/compare-results | Retrieve past results | Required |
| GET | /health | Service health + dependency status | Public |
| GET | /docs | Swagger UI | Public |

## Running Locally

```bash
cd "DERAI/FastAPI services"
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

## Testing

```bash
pytest tests/ -v --tb=short
```
