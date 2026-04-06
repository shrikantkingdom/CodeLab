# DERAI — Document Extraction, Review & AI

A microservices-based system for PDF document extraction, AI-powered classification, and database comparison. Built with **FastAPI**, **Spring Boot**, and **React**.

## Tech Stack

| Service | Technology | Port |
|---------|-----------|------|
| **FastAPI** | Python 3.11, FastAPI, PyMuPDF, Tesseract OCR, Azure AI | `8000` |
| **Spring Boot** | Java 17, Spring Boot 3.x, Pegbox, PDFBox | `8080` |
| **React UI** | React 18, TypeScript, Vite, Material UI | `3000` |

## Architecture

```
┌──────────┐     ┌──────────────┐     ┌───────────────┐
│ React UI │────▶│   FastAPI     │────▶│  Spring Boot  │
│ :3000    │     │   :8000       │     │  :8080        │
└──────────┘     └──────┬───────┘     └───────────────┘
                        │
                 ┌──────┴───────┐
                 │  AI / OCR /  │
                 │  Snowflake / │
                 │  DB2         │
                 └──────────────┘
```

## Prerequisites

- **Docker Desktop** (v4.x+) — [Download](https://www.docker.com/products/docker-desktop/)
- **Docker Compose** v2 (included with Docker Desktop)

> **Note:** Use `docker compose` (with a space), NOT `docker-compose` (the V1 standalone binary is deprecated).

### For local development (without Docker)

- Python 3.11+
- Java 17+ (JDK)
- Node.js 20+
- Maven 3.9+

---

## Quick Start (Docker — Recommended)

### 1. Clone & navigate

```bash
cd DERAI
```

### 2. Create environment file

```bash
cp .env.example .env
```

Edit `.env` if you have real credentials. All external services (Snowflake, DB2, OpenAI, Azure OCR) default to **mock mode** when credentials are empty — you can run the full system without any accounts.

### 3. Start Docker Desktop

Open **Docker Desktop** from your Applications and wait until the whale icon is steady (daemon is ready).

Verify:
```bash
docker compose version
# Expected: Docker Compose version v5.x.x

docker info | grep "Server Version"
# Expected: Server Version: 29.x.x (any version)
```

### 4. Build & run all services

```bash
docker compose up --build
```

This builds and starts all 3 services. First build takes a few minutes (downloads dependencies).

### 5. Verify services are running

```bash
# Health checks
curl http://localhost:8000/health    # FastAPI
curl http://localhost:8080/health    # Spring Boot

# Open React UI
open http://localhost:3000
```

### 6. Test the API

```bash
# Process a single document (mock mode)
curl -X POST http://localhost:8000/api/v1/process-single \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key-change-me" \
  -d '{
    "account_number": "ACC-001",
    "pdf_url": "https://example.com/sample.pdf",
    "extraction_engine": "pymupdf"
  }'
```

### 7. Stop services

```bash
docker compose down
```

---

## Running Locally (Without Docker)

### FastAPI Service

```bash
cd "FastAPI services"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Spring Boot Service

```bash
cd "Springboot services"

# Build & run
./mvnw spring-boot:run
```

API: http://localhost:8080/health

### React UI

```bash
cd "React UI"

# Install dependencies
npm install

# Run dev server
npm run dev
```

UI: http://localhost:3000

---

## Extraction Engines

| Engine | Type | Service | Description |
|--------|------|---------|-------------|
| `pymupdf` | Standard | FastAPI | Fast text extraction via PyMuPDF |
| `pdfplumber` | Standard | FastAPI | Table-aware extraction |
| `tika` | Standard | FastAPI | Apache Tika parser |
| `pegbox` | Java | Spring Boot | Proprietary Pegbox library |
| `pdfbox` | Java | Spring Boot | Apache PDFBox |
| `ocr_pytesseract` | OCR | FastAPI | All pages through Tesseract OCR |
| `ocr_azure` | OCR | FastAPI | All pages through Azure AI |
| `hybrid_pytesseract` | Hybrid | FastAPI | Smart routing — OCR only for image pages |
| `hybrid_azure` | Hybrid | FastAPI | Smart routing — Azure OCR for image pages |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | `dev-api-key-change-me` | API authentication key |
| `OPENAI_API_KEY` | No | _(empty = mock)_ | OpenAI key for AI classification |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model |
| `SNOWFLAKE_ACCOUNT` | No | _(empty = mock)_ | Snowflake account |
| `DB2_HOST` | No | _(empty = mock)_ | DB2 hostname |
| `AZURE_DOC_ENDPOINT` | No | _(empty = mock)_ | Azure Document Intelligence endpoint |
| `AZURE_DOC_API_KEY` | No | _(empty = mock)_ | Azure Document Intelligence key |
| `LOG_LEVEL` | No | `INFO` | Logging level |

See [.env.example](.env.example) for the full list.

---

## Project Structure

```
DERAI/
├── FastAPI services/        # Python extraction & orchestration service
│   ├── app/
│   │   ├── api/             # REST endpoints
│   │   ├── models/          # Pydantic models & enums
│   │   ├── services/
│   │   │   ├── pdf_extraction/
│   │   │   │   ├── ocr/     # OCR engines (pytesseract, Azure, hybrid)
│   │   │   │   ├── factory.py
│   │   │   │   └── *.py     # Extraction strategies
│   │   │   ├── ai_classification/
│   │   │   ├── comparison/
│   │   │   └── orchestrator.py
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── Springboot services/     # Java extraction service
│   ├── src/main/java/...
│   ├── Dockerfile
│   └── pom.xml
├── React UI/                # Frontend dashboard
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docs/                    # Comprehensive documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Documentation

Detailed docs are in the [docs/](docs/) folder:

- [Architecture](docs/architecture.md) — System design, patterns, data flow
- [FastAPI Service](docs/fastapi-service.md) — Python service deep dive
- [Spring Boot Service](docs/springboot-service.md) — Java service details
- [React UI](docs/react-ui.md) — Frontend architecture
- [OCR Strategy](docs/ocr-strategy.md) — Hybrid OCR approach
- [API Contracts](docs/api-contracts.md) — Full API specifications
- [Database Strategy](docs/database-strategy.md) — Snowflake & DB2
- [DevOps](docs/devops.md) — Docker, CI/CD, deployment
- [Interview Q&A](docs/interview-qa.md) — 60+ questions with answers

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `docker-compose: command not found` | Use `docker compose` (V2 syntax, with a space) |
| `failed to connect to docker API` | Open Docker Desktop and wait for daemon to start |
| `docker info` shows no Server Version | Docker Desktop is still starting — wait 30-60s |
| Port already in use | `docker compose down` first, or change ports in `docker-compose.yml` |
| Spring Boot build fails | Ensure Java 17+ with `java -version` |
| `ModuleNotFoundError` in FastAPI | Run `pip install -r requirements.txt` in venv |
