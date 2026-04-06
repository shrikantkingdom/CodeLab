# System Architecture — DERAI

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          REACT UI (Port 3000)                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ SingleInput  │  │ ExcelUpload  │  │ Engine    │  │ Comparison   │  │
│  │ Form        │  │ (Batch)      │  │ Selector  │  │ Table        │  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬─────┘  └──────────────┘  │
└─────────┼────────────────┼────────────────┼───────────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │ Axios → /api/v1/*
                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FASTAPI ORCHESTRATOR (Port 8000)                     │
│                                                                         │
│  ┌─── API Layer ──────────────────────────────────────────────────┐    │
│  │  POST /process-single   POST /process-batch                    │    │
│  │  GET  /compare-results  GET  /health                           │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌─── Orchestrator Pipeline ──────────────────────────────────────┐    │
│  │                                                                 │    │
│  │  1. PDF Download    → External PDF API (mock/real)              │    │
│  │  2. PDF Extraction  → Strategy: PyMuPDF | pdfplumber | Tika    │    │
│  │     ├── OCR         → pytesseract | Azure Doc Intelligence     │    │
│  │     ├── Hybrid      → text pages + OCR image pages             │    │
│  │     └── Java        → Spring Boot (Pegbox/PDFBox)              │    │
│  │  3. AI Classify     → OpenAI GPT-4o → structured JSON          │    │
│  │  4. DB Fetch        → Snowflake (statements) | DB2 (letters)   │    │
│  │  5. Compare         → Field-by-field match/mismatch/confidence │    │
│  │                                                                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                           │                                             │
│                  httpx (base64 PDF)                                     │
│                           │                                             │
└───────────────────────────┼─────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  SPRING BOOT SERVICE (Port 8080)                        │
│                                                                         │
│  ┌─── Controller ─────────────────────────────────────────────────┐    │
│  │  POST /extract/pdf    GET /health                              │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌─── Service Layer ──────────────────────────────────────────────┐    │
│  │  PegboxExtractorService (@Primary)                              │    │
│  │     └── Fallback → PdfBoxExtractorService (Apache PDFBox)       │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Design Patterns Used

| Pattern | Where | Why |
|---------|-------|-----|
| **Strategy** | PDF Extraction Factory | Pluggable extraction engines without modifying orchestrator |
| **Factory** | ExtractorFactory, DBFactory | Centralized object creation based on configuration |
| **Template Method** | OCR base class | Common OCR interface with engine-specific implementation |
| **Adapter** | SpringBootExtractor | Wraps Java service behind Python PDFExtractor interface |
| **Facade** | Orchestrator | Single entry point coordinates 5-step pipeline |
| **Observer** | React Query | Auto-refresh health status every 30 seconds |

## Data Flow — Single Document Processing

```
User submits form (account: 001-123456, type: statement, engine: hybrid_pytesseract)
  │
  ├── React UI → POST /api/v1/process-single
  │
  ├── FastAPI receives request
  │   ├── Validates input (Pydantic)
  │   ├── Auth middleware checks X-API-Key
  │   └── Routes to Orchestrator.process_single()
  │
  ├── Step 1: PDF Download
  │   └── httpx GET → external PDF API → receives PDF bytes
  │
  ├── Step 2: PDF Extraction (Hybrid OCR)
  │   ├── PyMuPDF opens PDF → classifies each page
  │   ├── Page 1: text-dominant → PyMuPDF extracts directly
  │   ├── Page 2: image scan → pytesseract OCR
  │   ├── Page 3: text-dominant → PyMuPDF extracts directly
  │   └── Merges all pages into unified text
  │
  ├── Step 3: AI Classification
  │   ├── Sends merged text to OpenAI GPT-4o
  │   ├── Prompt template for "statement" document type
  │   └── Returns structured JSON: {account_name, balance, date, ...}
  │
  ├── Step 4: Database Fetch
  │   ├── DocumentType=statement → SnowflakeConnector
  │   └── Query: SELECT * WHERE office='001' AND account='123456'
  │
  ├── Step 5: Comparison
  │   ├── Field mapping: pdf.account_name ↔ db.ACCT_NAME
  │   ├── Compares each field: exact match / fuzzy (Jaccard > 0.9)
  │   └── Returns: ComparisonResult with match/mismatch/confidence
  │
  └── Response → React UI → renders ComparisonTable
```

## Service Communication

| From | To | Protocol | Auth | Purpose |
|------|----|----------|------|---------|
| React UI | FastAPI | HTTP REST | X-API-Key | All user requests |
| FastAPI | Spring Boot | HTTP REST | X-API-Key | Java PDF extraction |
| FastAPI | External PDF API | HTTP/HTTPS | API Key | Download PDFs |
| FastAPI | OpenAI | HTTPS | Bearer token | AI classification |
| FastAPI | Snowflake | Snowflake connector | User/password | Statement data |
| FastAPI | DB2 | JDBC via ibm_db | User/password | Letter/confirm data |
| FastAPI | Azure | HTTPS | API Key | Azure OCR |

## Security Model

1. **API Key Authentication**: All inter-service calls use `X-API-Key` header
2. **Public paths excluded**: `/health`, `/docs`, `/swagger-ui`, `/api-docs`
3. **CORS**: Only `localhost:3000` allowed in development
4. **No credentials in code**: All secrets via environment variables / `.env` file
5. **Non-root Docker containers**: All Dockerfiles use non-root users
6. **Input validation**: Pydantic models validate all request bodies
7. **Future**: OAuth2/JWT for production, API rate limiting

## Scalability Considerations

1. **Horizontal**: FastAPI is stateless — scale with multiple containers behind load balancer
2. **Async**: FastAPI uses async/await — handles concurrent requests efficiently
3. **Batch**: `asyncio.gather` for parallel processing of batch requests
4. **Caching**: Comparison results stored in memory (upgrade to Redis)
5. **Queue**: Celery/RabbitMQ for heavy batch jobs (future)
