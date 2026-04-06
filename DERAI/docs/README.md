# DERAI — Document Extraction, Review & AI
## Complete Project Documentation

### 📁 Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture Overview](./architecture.md) | System architecture, service communication, data flow |
| [FastAPI Service](./fastapi-service.md) | Python backend — PDF extraction, AI classification, comparison |
| [Spring Boot Service](./springboot-service.md) | Java backend — Pegbox/PDFBox extraction |
| [React UI](./react-ui.md) | Frontend — Material UI dashboard |
| [OCR Strategy](./ocr-strategy.md) | Hybrid OCR: pytesseract, Azure, page-level routing |
| [Database Strategy](./database-strategy.md) | Snowflake & DB2 connectivity, mock strategy |
| [API Contracts](./api-contracts.md) | REST API specifications across all services |
| [DevOps & Deployment](./devops.md) | Docker, CI/CD, environment setup |
| [Challenges & Solutions](./challenges.md) | Engineering challenges faced and overcome |
| [Future Enhancements](./future-enhancements.md) | Roadmap and open items |
| [AI Providers & Model Selection](./ai-providers-guide.md) | 6 AI providers, model lists, API key setup, runtime selection |
| [AWS Cloud Deployment](./aws-deployment.md) | 3 deployment plans (EC2, ECS Fargate, EKS), CI/CD, cost estimates |
| [AWS Deployment Prompt](./aws-deployment-prompt.md) | Ready-to-use prompt for implementing AWS deployment |
| [Interview Q&A](./interview-qa.md) | 60+ interview questions with detailed answers |
| [GitHub Repository Strategy](./github-repos.md) | 3-repo structure, branching, GitHub Actions |

---

### Quick Start

```bash
# Clone all 3 repos (or monorepo approach)
cd DERAI/

# Copy environment file
cp .env.example .env

# Start all services
docker compose up --build

# Access:
#   React UI:     http://localhost:3000
#   FastAPI Docs: http://localhost:8000/docs
#   Spring Boot:  http://localhost:8080/swagger-ui.html
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 18 + TypeScript + Vite | QA/Ops dashboard |
| Backend (Python) | FastAPI + Python 3.11 | Orchestration, AI, DB comparison |
| Backend (Java) | Spring Boot 3.x + Java 17 | PDF extraction (Pegbox/PDFBox) |
| AI/ML | OpenAI GPT-4o | Structured data extraction from text |
| OCR | pytesseract / Azure Doc Intelligence | Image-heavy page extraction |
| Database | Snowflake + DB2 | Financial records storage |
| DevOps | Docker Compose + GitHub Actions | Containerization + CI/CD |
