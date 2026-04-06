# DERAI — Technical Architect Suggestions

## Architecture Assessment (Current State: 8/10)

The current architecture is well-designed for its scale. Here are specific suggestions from a technical architect perspective:

---

## 1. Event-Driven Architecture (Priority: High)

**Current**: Synchronous request-response for everything, including batch processing.

**Suggestion**: Add an event bus for decoupling:

```
                         ┌──────────────┐
POST /process-batch  →   │  Event Bus   │  → Worker Pool
                         │ (Redis/NATS) │
                         └──────┬───────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              Worker 1    Worker 2    Worker 3
              (extract)   (extract)   (extract)
                    │           │           │
                    └───────────┼───────────┘
                                │
                         Result Store → WebSocket → UI
```

**Benefit**: Batch processing becomes non-blocking. Workers can be scaled independently.
**Implementation**: Celery + Redis (Python native), or NATS for polyglot.

---

## 2. Circuit Breaker Pattern (Priority: High)

**Current**: Direct HTTP calls to Spring Boot, OpenAI, external PDF API with basic timeout.

**Suggestion**: Add circuit breaker with `tenacity` (Python) / Resilience4j (Java):

```python
from tenacity import retry, stop_after_attempt, wait_exponential, CircuitBreaker

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(httpx.ConnectError),
)
async def call_springboot(self, pdf_bytes):
    ...
```

**States**: Closed (normal) → Open (after 3 failures, skip calls for 30s) → Half-Open (try one call)

---

## 3. CQRS for Comparison Results (Priority: Medium)

**Current**: Process and query go through the same path.

**Suggestion**: Separate write and read models:

```
Write: POST /process    → Orchestrator → Store in PostgreSQL/Redis
Read:  GET /results     → Read directly from optimized query store
```

**Benefit**: Query performance independent of processing complexity. Can add full-text search, filters, aggregations on the read side without affecting write performance.

---

## 4. API Gateway (Priority: Medium for Production)

**Current**: React calls FastAPI directly. Spring Boot is internal only.

**Suggestion**: Add API gateway (Kong, AWS API Gateway, or Nginx):

```
Internet → API Gateway → FastAPI (internal)
                       → Spring Boot (internal)
                       
Gateway handles:
- Rate limiting (100 req/min per API key)
- JWT validation
- Request logging
- API versioning (/v1, /v2)
- SSL termination
```

---

## 5. Observability Stack (Priority: High for Production)

**Current**: Structured JSON logs to stdout.

**Suggestion**: Full observability → Logs + Metrics + Traces:

| Layer | Tool | Purpose |
|-------|------|---------|
| Logs | Fluentd → Elasticsearch → Kibana | Searchable structured logs |
| Metrics | Prometheus → Grafana | Request latency, error rates, OCR timing |
| Traces | OpenTelemetry → Jaeger | Cross-service request tracking |
| Alerts | Grafana Alerts → PagerDuty | SLA violation detection |

**Key metrics to track**:
- `extraction_duration_seconds{engine="hybrid_pytesseract"}` — per-engine timing
- `ocr_confidence_score{engine="pytesseract"}` — OCR quality monitoring
- `comparison_match_rate{doc_type="statement"}` — business metric
- `external_api_error_rate{service="openai"}` — dependency health

---

## 6. Document Versioning & Audit Trail (Priority: High for Financial)

**Current**: No persistence of processing results.

**Suggestion**: Immutable audit log for regulatory compliance:

```sql
CREATE TABLE processing_audit (
    id UUID PRIMARY KEY,
    account_number VARCHAR(9) NOT NULL,
    document_type VARCHAR(20) NOT NULL,
    extraction_engine VARCHAR(30) NOT NULL,
    pdf_hash SHA256 NOT NULL,              -- Document fingerprint
    extracted_data JSONB NOT NULL,          -- AI classification result
    comparison_result JSONB NOT NULL,       -- Field-by-field comparison
    processing_time_ms INTEGER NOT NULL,
    processed_by VARCHAR(100) NOT NULL,     -- API key or user ID
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1              -- Re-processing creates new version
);
```

**Why**: Financial regulations (SOX, SOC2) require audit trails. This also enables trend analysis and model improvement.

---

## 7. Feature Flags (Priority: Medium)

**Current**: Engine selection is per-request. No gradual rollout capability.

**Suggestion**: LaunchDarkly or simple DB-backed feature flags:

```python
if feature_flag.is_enabled("azure-ocr-v2", user=api_key):
    engine = "azure_doc_intelligence_v2"
else:
    engine = "azure_doc_intelligence_v1"
```

**Use cases**:
- Gradually roll out new OCR model to 10% of requests
- A/B test pytesseract vs Azure accuracy
- Kill switch for problematic engines

---

## 8. API Versioning Strategy (Priority: Low Now, High at Scale)

**Current**: `/api/v1/` prefix.

**Suggestion**: Plan for v2 now:
- **URL versioning**: `/api/v2/process-single` (current approach, keep it)
- **Backward compatibility**: v1 calls internally transform to v2 format
- **Deprecation process**: v1 returns `Sunset: Sat, 01 Jan 2028 00:00:00 GMT` header
- **Client SDK**: Auto-generated from OpenAPI spec

---

## 9. Idempotency (Priority: High)

**Current**: Reprocessing the same document creates a new result every time.

**Suggestion**: Idempotency keys prevent duplicate processing:

```python
@app.post("/process-single")
async def process_single(request: ProcessRequest, idempotency_key: str = Header(None)):
    if idempotency_key:
        cached = await redis.get(f"idempotent:{idempotency_key}")
        if cached:
            return cached  # Return identical result
    result = await orchestrator.process_single(request)
    if idempotency_key:
        await redis.setex(f"idempotent:{idempotency_key}", 86400, result)
    return result
```

---

## 10. Data Pipeline for ML Training (Priority: Long-term)

**Current**: AI classification uses OpenAI with no feedback loop.

**Suggestion**: Build a feedback pipeline:

```
Processing → Human Review → Labeled Data → Fine-tune Model → Deploy

Specifics:
1. QA analysts mark comparison results as "correct" or "incorrect"
2. Store corrected data as training set
3. Fine-tune LayoutLM or GPT-3.5 on domain-specific documents
4. Replace OpenAI with cheaper, faster, private model
```

**ROI**: Reduces OpenAI API costs by 90%, improves accuracy on domain-specific formats, eliminates external API dependency.
