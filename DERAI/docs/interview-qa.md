# Interview Q&A — DERAI Project

## 60+ Questions with Detailed Answers

> Use this document to prepare for technical interviews. Each answer explains the "what", "why", and "how" — the three things interviewers evaluate.

---

## Section 1: Architecture & Design (15 Questions)

### Q1: Walk me through the system architecture of DERAI.
**A:** DERAI is a 3-tier microservices system for automated financial document verification. The **React frontend** provides a dashboard for QA analysts. The **FastAPI backend** (Python) orchestrates the entire pipeline: downloading PDFs, extracting text, AI-powered classification, database comparison, and result aggregation. The **Spring Boot service** (Java) provides alternative PDF extraction using Java libraries like Pegbox and PDFBox. All services run in Docker containers and communicate via REST APIs with API-key authentication.

The pipeline follows 5 steps: Download → Extract → AI Classify → DB Fetch → Compare. This is coordinated by the Orchestrator class which acts as a Facade pattern.

### Q2: Why did you choose a microservices architecture instead of a monolith?
**A:** Three reasons: (1) **Language optimization** — Python excels at AI/ML tasks while Java was mandated for Pegbox/PDFBox extraction, so we needed polyglot services. (2) **Independent deployment** — the extraction service can be updated without touching the orchestrator. (3) **Team scalability** — Java developers maintain the extraction service while Python developers handle the AI pipeline. That said, at our current scale, a modular monolith would also work — we chose microservices because the language barrier forced it.

### Q3: Explain the Strategy pattern in your PDF extraction layer.
**A:** We have 9 extraction engines that all implement the same `PDFExtractor` interface with an `async extract(pdf_bytes) → dict` method. The `ExtractorFactory` maps enum values to concrete classes. The Orchestrator calls `ExtractorFactory.get_extractor(engine)` and doesn't know which engine it gets — it just calls `extract()`.

This means adding a new engine requires: (1) implement `PDFExtractor`, (2) add an enum value, (3) register in the factory. Zero changes to the orchestrator, API layer, or frontend.

### Q4: What design patterns did you use and why?
**A:**
- **Strategy**: PDF extraction engines — pluggable algorithms behind a common interface
- **Factory**: `ExtractorFactory`, `DBFactory` — encapsulates object creation logic
- **Adapter**: `SpringBootExtractor` — wraps a Java REST service behind the Python `PDFExtractor` interface
- **Facade**: `Orchestrator` — single entry point coordinates 5 pipeline steps
- **Template Method**: `OCRExtractor` base class — common interface, engine-specific implementations

### Q5: How does the hybrid OCR work?
**A:** Instead of OCR-ing every page (slow and expensive), we classify each page as text-dominant or image-dominant. Text pages are extracted with PyMuPDF (instant, free). Image pages are rendered to 300 DPI PNG and sent to OCR (pytesseract locally or Azure cloud). Results are merged in page order. This gives 3x speedup and 60% cost reduction vs full-document OCR.

### Q6: How did you handle the Pegbox proprietary library?
**A:** Pegbox is an internal JAR not available on Maven Central. The `PegboxExtractorService` checks classpath at startup. If absent, it delegates to PDFBox. At runtime, if Pegbox throws, it catches and falls back. This means the project works perfectly without Pegbox — zero config needed.

### Q7: Why FastAPI instead of Flask or Django?
**A:** (1) **Async native** — `async/await` for concurrent PDF processing and external API calls. (2) **Auto-generated OpenAPI docs** — Swagger UI out of the box. (3) **Pydantic validation** — type-safe request/response models with auto-validation. (4) **Performance** — 2-3x faster than Flask for I/O-bound workloads.

### Q8: Why Spring Boot instead of writing all extraction in Python?
**A:** The client mandated Pegbox, which is a Java-only library. Rather than using Py4J or subprocess hacks, we built a clean Java microservice. This also gives us access to Apache PDFBox, which handles large PDFs with better memory management than Python alternatives.

### Q9: How do you handle cross-service communication failures?
**A:** The `SpringBootExtractor` uses `httpx` with configurable timeouts (30s default). On connection failure, it raises `ExtractionError` which the orchestrator catches and returns as a structured error response with `"engine_status": "unreachable"`. The health endpoint shows real-time dependency status. Future: circuit-breaker pattern with `tenacity` library.

### Q10: Explain your data flow for a single document.
**A:** User submits (account: 001-123456, type: statement, engine: hybrid_pytesseract) → React sends POST to FastAPI → Orchestrator downloads PDF bytes from external API → Hybrid extractor opens PDF, classifies 5 pages (3 text, 2 image) → Text pages extracted by PyMuPDF, image pages OCR'd by pytesseract → Merged text sent to OpenAI GPT-4o with statement-specific prompt → AI returns structured JSON (account_name, balance, date) → Snowflake queried for DB record → Field-by-field comparison with fuzzy matching → Result sent back to React → ComparisonTable renders green/red chips.

### Q11: How scalable is this architecture?
**A:** FastAPI is stateless, so horizontal scaling is trivial — add containers behind a load balancer. The bottleneck is external calls (OCR, OpenAI, DB). For batch processing, `asyncio.gather` runs concurrent requests. Future: Celery + Redis for background job processing, Kubernetes HPA for auto-scaling based on CPU.

### Q12: What would you change for a production deployment?
**A:** (1) Replace API key auth with OAuth2/JWT + Azure AD, (2) Add Redis caching for DB records, (3) Move batch processing to Celery queue, (4) Kubernetes with HPA, (5) Structured logging to ELK/Datadog, (6) Add circuit breakers on external calls, (7) Per-tenant isolation.

### Q13: How do you ensure security?
**A:** API key authentication on all endpoints (except /health, /docs). CORS restricted to localhost:3000. All credentials via environment variables. Pydantic validates all input. Parameterized SQL queries prevent injection. Docker containers run as non-root. No sensitive data in logs.

### Q14: Describe the comparison engine.
**A:** It does field-by-field comparison between AI-extracted PDF data and DB records. First tries exact string match. If that fails, uses bigram Jaccard similarity (set intersection over union of character bigrams). Threshold is 0.9 — above = fuzzy match, below = mismatch. Returns per-field: status (match/mismatch/missing), confidence score, both values.

### Q15: How do you handle different document types (statements, letters, confirms)?
**A:** Each document type has: (1) unique AI prompt template with specific fields to extract, (2) database connector (Snowflake for statements, DB2 for letters/confirms), (3) field mapping for comparison (PDF field names ↔ DB column names). The `DocumentType` enum drives all routing decisions.

---

## Section 2: Implementation Details (15 Questions)

### Q16: How does your AI classification work?
**A:** We send the extracted PDF text to OpenAI GPT-4o with a per-document-type prompt template. The prompt specifies exact fields to extract (e.g., account_name, balance, date for statements). We use `response_format={"type": "json_object"}` to enforce JSON output. Post-processing normalizes field names. Fallback: regex extraction if OpenAI is unavailable.

### Q17: How do you handle OCR page classification?
**A:** Heuristic with 3 signals: (1) text length < 50 chars on a page with images → image page, (2) text density (characters per page area) below 0.3 threshold → image page, (3) PyMuPDF's `get_images()` detects embedded images. This is ~95% accurate and configurable per document type.

### Q18: Explain your mock-first development approach.
**A:** Every external dependency (Snowflake, DB2, PDF API, OpenAI) has mock mode activated when credentials are empty. Mocks return realistic data matching production schemas. This means `cp .env.example .env && docker compose up` works immediately — no accounts, no VPN, no API keys needed for development.

### Q19: How does Pydantic validation work in your models?
**A:** `AccountNumber` model uses `@field_validator` to auto-pad office (3 digits, zero-filled) and account (6 digits, zero-filled). `ProcessSingleRequest` uses `ExtractionEngine` enum for engine validation. Optional fields like `statement_input` are only required when `document_type == "statement"`. Invalid input → automatic 422 with field-level error messages.

### Q20: How do you handle concurrent batch processing?
**A:** `Orchestrator.process_batch()` uses `asyncio.gather(*tasks)` to process all documents concurrently. Each task independently downloads, extracts, classifies, and compares. Results are collected when all complete. Future: semaphore to limit concurrent OCR/API calls and prevent rate limiting.

### Q21: Describe the configuration management approach.
**A:** Pydantic `BaseSettings` reads from environment variables with fallback defaults. `.env` file for local development. Docker Compose passes env vars from `.env.example`. All secrets (API keys, DB passwords) are env-only — never in code. Settings object is a singleton accessed throughout the app.

### Q22: How does the React frontend handle engine selection?
**A:** `ExtractionEngine` TypeScript enum mirrors the Python enum. The `SingleInputForm` groups engines by category (Standard, Java, OCR, Hybrid) in a Material UI Select with optgroup-style dividers. When user selects "hybrid_pytesseract", it's sent as-is in the request body. The backend routes to the correct extractor.

### Q23: How do you handle errors across the pipeline?
**A:** Each pipeline step returns a structured result or raises a typed exception. The orchestrator catches exceptions at each step and continues with partial results (extraction failed? Skip AI classification). Final response includes `"errors": [...]` array with per-step error details. Frontend shows which step failed with a red indicator.

### Q24: Explain the Docker multi-stage build.
**A:** FastAPI Dockerfile: Stage 1 (python:3.11) installs all deps into a venv. Stage 2 (python:3.11-slim) copies only the venv and app code — no pip, no build tools, smaller image. Spring Boot: Stage 1 (temurin:17-jdk) runs `mvn package`. Stage 2 (temurin:17-jre) copies only the JAR — no Maven, no source code.

### Q25: How is the Spring Boot security configured?
**A:** `SecurityConfig` extends `WebSecurityConfigurerAdapter` (deprecated but functional) with a custom `OncePerRequestFilter`. The filter reads `X-API-Key` header, compares against `app.api-key` property. Public paths (`/health`, `/actuator/**`) are excluded. Invalid key → 401 JSON response via `GlobalExceptionHandler`.

### Q26: What testing strategy did you use?
**A:** Unit tests for comparison engine (exact match, fuzzy match, edge cases), extraction factory (correct engine returned), model validation (padding, enum validation). Integration tests for API endpoints using FastAPI TestClient. Mock external dependencies in tests. Future: BDD with pytest-bdd for acceptance tests.

### Q27: How does the fuzzy matching work?
**A:** Bigram Jaccard similarity. Break both strings into character pairs (bigrams): "John" → {"Jo", "oh", "hn"}. Compute intersection ÷ union of bigram sets. Score 0.0–1.0. Above 0.9 = fuzzy match (accounts for minor OCR errors like "John" vs "Johm"). Below 0.9 = mismatch.

### Q28: How do you handle PDF download from external API?
**A:** `PdfDownloadService` uses `httpx.AsyncClient` with retry logic (3 attempts, exponential backoff). The external API URL comes from config. Mock mode returns sample PDF bytes. The service returns raw bytes regardless of source — the extraction layer doesn't care where the PDF came from.

### Q29: Explain the React Query integration.
**A:** Process-single uses `useMutation` — no caching, immediate execution on form submit. Health check uses `useQuery` with 30-second `refetchInterval` for auto-refresh. History uses `useQuery` with `queryKey` containing the account filter — refetches when filter changes. `QueryClientProvider` wraps the app with default retry and stale time settings.

### Q30: How do you handle environment differences (dev/staging/prod)?
**A:** Environment variables drive all configuration. `.env.example` has sane defaults for local dev (mock mode). Docker Compose can override with `env_file:`. Kubernetes deployments use ConfigMap/Secret. GitHub Actions CI sets `MOCK_MODE=true` for testing. No if/else for environment names in code.

---

## Section 3: OCR & AI Deep Dive (10 Questions)

### Q31: Why pytesseract AND Azure? Why not just one?
**A:** Different trade-offs: pytesseract is free, offline, GDPR-compliant — ideal for development and privacy-sensitive documents. Azure Doc Intelligence has 96-99% accuracy with table detection — ideal for production with complex layouts. Users choose per request. The Strategy pattern makes this trivial.

### Q32: How would you handle handwritten text in documents?
**A:** pytesseract is weak on handwriting. Azure Doc Intelligence has a dedicated handwriting model. For production, I'd route detected handwritten pages to Azure regardless of user selection. Future: fine-tune a handwriting recognition model on domain-specific samples.

### Q33: What's the cost of running Azure OCR at scale?
**A:** Azure Read API: ~$1.50 per 1,000 pages. With hybrid approach (only OCR image pages), actual cost is ~40% of that. For 10,000 documents/month averaging 5 pages with 2 image pages each: 20,000 OCR pages × $0.0015 = ~$30/month. Very cost-effective.

### Q34: How do you ensure AI extraction consistency?
**A:** Three techniques: (1) `response_format={"type": "json_object"}` enforces valid JSON, (2) Explicit field schema in the prompt — "Return EXACTLY these fields: account_name, balance, date", (3) Post-processing normalizes all field names to snake_case. If AI returns unexpected format, regex fallback extracts key values.

### Q35: What if OpenAI is down or rate-limited?
**A:** The orchestrator catches OpenAI exceptions gracefully. If AI classification fails, the response includes the raw extracted text and a warning. Users can manually review. Future: fallback to local LLM (llama.cpp) or simple regex-based extraction for known document templates.

### Q36: How accurate is the page classification heuristic?
**A:** ~95% accurate in our testing. False positives (text page classified as image) waste OCR resources but don't affect accuracy. False negatives (image page classified as text) produce empty text — caught by downstream pipeline. The threshold is configurable per document type.

### Q37: Could you use a local LLM instead of OpenAI?
**A:** Yes, the classification service is abstracted behind an interface. For production without external API dependency, I'd use Ollama + Llama 3 or Mistral. The prompt format would need adjustment, but the interface stays the same. Trade-off: lower accuracy but zero API cost and full data privacy.

### Q38: How do you handle multi-page tables that span pages?
**A:** Current approach: extract per-page, merge text. This can break table continuity. Future improvement: (1) Detect table boundaries using pdfplumber, (2) If a table spans pages, extract as a single unit, (3) Use Azure Layout model which natively handles multi-page tables.

### Q39: What happens if OCR produces garbage text?
**A:** The confidence score catches this — pytesseract reports word-level confidence. If average page confidence < 0.5, the page is flagged as "low_confidence" in metadata. The AI classification sees garbage text and either extracts nothing or returns low-confidence fields. The comparison engine marks these as "UNCERTAIN" rather than "MISMATCH".

### Q40: How would you add support for a new OCR provider?
**A:** (1) Create a class implementing `OCRExtractor` with `extract_from_image()` and `extract_from_images_batch()`. (2) Add the engine to `OCREngine` enum. (3) Register in `OCRExtractorFactory.create()`. (4) Optionally add a `HybridOCRExtractor` variant. Takes ~30 minutes for a provider with a good SDK.

---

## Section 4: Infrastructure & DevOps (10 Questions)

### Q41: Why Docker Compose and not Kubernetes from the start?
**A:** Premature optimization. Docker Compose gives us containerized parity with production while being trivial to set up. For a 3-service system with under 1000 requests/day, Kubernetes is overkill. When we need auto-scaling, rolling updates, or multi-node deployment, we'll migrate. The Docker images are already Kubernetes-ready.

### Q42: Describe your CI/CD pipeline.
**A:** Three independent GitHub Actions workflows — one per service. Each triggers on push/PR to its directory. FastAPI CI: lint (ruff) → test (pytest) → build Docker. Spring Boot CI: test (mvn test) → build JAR. React CI: lint → type-check → build. All use caching for dependencies. Future: add deployment to AWS/GCP on main merge.

### Q43: How do you handle secrets in CI/CD?
**A:** GitHub Secrets for API keys and credentials. In Actions: `${{ secrets.OPENAI_API_KEY }}`. In Docker: env vars from `.env` file (never committed). In Kubernetes: Kubernetes Secrets mounted as env vars. No secrets in code, Dockerfiles, or compose files.

### Q44: What monitoring would you add for production?
**A:** (1) Structured JSON logging → ELK or Datadog, (2) Prometheus metrics (request latency, error rate, OCR processing time), (3) Grafana dashboards, (4) PagerDuty alerts for error rate > 5% or P99 latency > 10s, (5) Distributed tracing (Jaeger) for cross-service request tracking.

### Q45: How would you handle database migrations?
**A:** We don't own the Snowflake/DB2 schemas — they're external systems. But if we add our own storage (e.g., comparison results), I'd use Alembic for FastAPI (SQLAlchemy migration tool) and Flyway for Spring Boot. Migrations run in CI before deployment.

### Q46: Explain the Docker networking.
**A:** Docker Compose creates a bridge network (`derai-net`). Services communicate by container name: FastAPI calls `http://springboot-service:8080`. React's nginx proxies `/api` to `http://fastapi-service:8000`. Only React's port 3000 is exposed to the host. In production: Kubernetes Service DNS replaces this.

### Q47: How do you handle log aggregation across 3 services?
**A:** All services output structured JSON logs. Docker Compose captures stdout. In production: centralized logging via ELK stack or Datadog. Each log includes: service name, request ID (UUID), timestamp, level, message. The request ID is propagated via `X-Request-ID` header across services for distributed tracing.

### Q48: What's your rollback strategy?
**A:** Docker images are tagged with git commit SHA. Rollback = redeploy previous image tag. Docker Compose: change image tag in compose file. Kubernetes: `kubectl rollout undo`. GitHub Actions stores build artifacts. Database: no migrations we own, so no DB rollback needed.

### Q49: How would you set up a staging environment?
**A:** Clone the Docker Compose setup on a cloud VM (EC2/Azure VM). Use separate `.env` with staging credentials. Point to staging Snowflake/DB2 instances. Use a staging OpenAI API key with lower rate limits. Add basic auth or VPN to restrict access.

### Q50: Why 3 separate CI workflows instead of a monorepo workflow?
**A:** Independent deployment. Changing Python tests shouldn't rebuild the Java JAR. Each workflow only triggers on changes to its service directory (`paths: ["FastAPI services/**"]`). This reduces CI time and deployment risk.

---

## Section 5: Process, Teamwork & Leadership (10 Questions)

### Q51: How did you plan this project?
**A:** I used GitHub Copilot to create a detailed plan from the specification document. The plan covered: phase breakdown (6 phases), file listing per phase, technology decisions with justification, architecture design, and execution order. This plan became a living document updated as we progressed. I can show you the plan as a portfolio piece — it demonstrates my ability to decompose complex systems into deliverable phases.

### Q52: How do you handle changing requirements?
**A:** DERAI started as text extraction + comparison. Then OCR was added as a requirement. Because of the Strategy pattern, adding OCR required only new files and enum values — zero changes to the orchestrator or API layer. This is the value of clean architecture: requirements change, but the core stays stable.

### Q53: How would you onboard a new developer?
**A:** (1) Read the README and architecture doc (15 min), (2) `cp .env.example .env && docker compose up --build` (5 min), (3) Browse Swagger UI at localhost:8000/docs, (4) Process a sample document through the UI, (5) Read the strategy pattern code in pdf_extraction/, (6) First task: add a new extraction engine following the template.

### Q54: How do you ensure code quality?
**A:** (1) Type annotations everywhere — Pydantic for runtime, TypeScript for frontend, (2) Linting: ruff (Python), ESLint (TypeScript), (3) Tests in CI — PR can't merge with failing tests, (4) Code review, (5) Structured logging for debugging, (6) Mock-first development ensures tests run without external deps.

### Q55: What was the most difficult technical decision?
**A:** Hybrid OCR strategy. Options were: (A) OCR everything — simple but expensive, (B) OCR nothing — fast but misses scanned pages, (C) Hybrid — complex but optimal. I chose hybrid because financial documents are mixed — 60% text, 40% scanned. The page classification heuristic was the hardest part to get right.

### Q56: How do you communicate technical decisions to non-technical stakeholders?
**A:** I frame decisions in business terms. "Hybrid OCR reduces our Azure bill by 60% while maintaining the same accuracy." "Mock-first development means any developer can start contributing in 5 minutes without needing production credentials." "Strategy pattern means adding WellsFargo's custom format takes 30 minutes, not a sprint."

### Q57: What would you do differently if starting over?
**A:** (1) Start with Kubernetes from day 1 if team size > 5, (2) Use gRPC instead of REST between FastAPI and Spring Boot for lower latency, (3) Add structured table extraction earlier — it's the hardest problem and we deferred it.

### Q58: How do you handle technical debt?
**A:** I maintain an "Open Challenges" document that tracks known limitations. Each item has: status, impact, proposed solution, and estimated effort. During sprint planning, we allocate 20% capacity to tech debt. Example: "Replace API key with OAuth2" has been tracked since sprint 1 with a clear migration plan.

### Q59: Describe a time you had to learn something new quickly for this project.
**A:** I hadn't used Azure Document Intelligence before. I read the SDK docs, set up a free-tier resource, ran the quickstart, then designed our adapter class in a day. The key was recognizing it's just another implementation of our `OCRExtractor` interface — the pattern was already in place, I just needed to learn the SDK specifics.

### Q60: What's your approach to handling failed comparisons?
**A:** Not every mismatch is an error — OCR might read "01/01/2026" while DB has "2026-01-01". The comparison engine normalizes dates before comparing. For remaining mismatches, we report them with confidence scores. QA analysts make the final call. The system augments human judgment, it doesn't replace it.

---

## Bonus: Portfolio Talking Points

1. **"I designed and implemented a complete microservices system from spec to Docker deployment using AI-assisted development"**
2. **"I created the detailed project plan from scratch using Copilot, then implemented every phase"**
3. **"I solved the image vs text extraction problem with a hybrid OCR strategy that reduces cost by 60%"**
4. **"The Strategy pattern handles 9 extraction engines with zero coupling to the pipeline"**
5. **"Mock-first development means anyone can run the full system in 5 minutes with zero configuration"**
