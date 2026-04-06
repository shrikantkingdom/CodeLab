# API Contracts

## FastAPI Service (Port 8000)

### POST /api/v1/process-single
Process a single document.

**Request Headers:**
```
X-API-Key: derai-dev-key-2026
Content-Type: application/json
```

**Request Body:**
```json
{
  "account": {
    "office": "001",
    "account_number": "123456"
  },
  "document_type": "statement",
  "extraction_engine": "hybrid_pytesseract",
  "statement_input": {
    "period_start": "2026-01-01",
    "period_end": "2026-03-31"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "account": "001-123456",
  "document_type": "statement",
  "extraction_engine": "hybrid_pytesseract",
  "extraction_result": {
    "raw_text": "Account Statement for ...",
    "page_count": 3,
    "ocr_metadata": {
      "total_pages": 3,
      "ocr_pages": 1,
      "text_pages": 2,
      "ocr_engine": "pytesseract"
    }
  },
  "ai_classification": {
    "account_name": "John Smith",
    "account_number": "001-123456",
    "statement_date": "2026-03-31",
    "beginning_balance": "50000.00",
    "ending_balance": "52340.50"
  },
  "db_record": {
    "ACCT_NAME": "John Smith",
    "ACCT_NUM": "001123456",
    "STMT_DT": "2026-03-31",
    "BEG_BAL": "50000.00",
    "END_BAL": "52340.50"
  },
  "comparison": {
    "overall_status": "MATCH",
    "match_count": 5,
    "mismatch_count": 0,
    "missing_count": 0,
    "fields": [
      {
        "field": "account_name",
        "pdf_value": "John Smith",
        "db_value": "John Smith",
        "status": "MATCH",
        "confidence": 1.0
      }
    ]
  }
}
```

### POST /api/v1/process-batch
Process multiple documents from Excel upload.

**Request Body:**
```json
{
  "accounts": [
    {"office": "001", "account_number": "123456"},
    {"office": "002", "account_number": "789012"}
  ],
  "document_type": "statement",
  "extraction_engine": "pymupdf"
}
```

**Response (200):**
```json
{
  "total": 2,
  "successful": 2,
  "failed": 0,
  "results": [ /* array of process-single responses */ ]
}
```

### GET /health
**Response (200):**
```json
{
  "service": "derai-fastapi",
  "status": "healthy",
  "dependencies": {
    "snowflake": "connected",
    "db2": "mock",
    "springboot": "unreachable",
    "openai": "configured"
  },
  "uptime_seconds": 3600,
  "version": "1.0.0"
}
```

---

## Spring Boot Service (Port 8080)

### POST /extract/pdf

**Request Headers:**
```
X-API-Key: derai-dev-key-2026
Content-Type: application/json
```

**Request Body:**
```json
{
  "pdfContent": "<base64-encoded-pdf>",
  "engine": "pdfbox"
}
```

**Response (200):**
```json
{
  "rawText": "Account Statement\n...",
  "extractedData": {},
  "pageCount": 3,
  "engineUsed": "pdfbox",
  "success": true,
  "extractionTimeMs": 245
}
```

### GET /health
```json
{
  "status": "healthy",
  "service": "derai-extraction-service",
  "version": "1.0.0"
}
```

---

## Error Response Format (Both Services)

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Account number must be 6 digits",
  "status": 400,
  "timestamp": "2026-04-05T10:30:00Z"
}
```

| Status | Error Type | Example |
|--------|-----------|---------|
| 400 | VALIDATION_ERROR | Invalid account format |
| 401 | UNAUTHORIZED | Missing/invalid API key |
| 404 | NOT_FOUND | Account not in database |
| 422 | EXTRACTION_FAILED | PDF could not be parsed |
| 500 | INTERNAL_ERROR | Unexpected server error |
