# GitHub Repository Strategy

## 3-Repo Structure

Separate repositories for independent deployment, CI/CD, and team ownership:

| Repository | Contents | Primary Language |
|-----------|----------|-----------------|
| `derai-fastapi` | FastAPI orchestrator + AI + OCR + DB | Python 3.11 |
| `derai-springboot` | Spring Boot extraction service | Java 17 |
| `derai-react-ui` | React + TypeScript dashboard | TypeScript |

### Additional Repos
| Repository | Contents |
|-----------|----------|
| `derai-infra` | docker-compose.yml, .env.example, Kubernetes manifests, Terraform |
| `derai-docs` | Technical documentation, architecture diagrams, runbooks |

## Repository Setup Plan

### Step 1: Create Repos
```bash
# Using GitHub CLI
gh repo create derai-fastapi --private --description "DERAI - FastAPI Orchestrator & AI Pipeline"
gh repo create derai-springboot --private --description "DERAI - Spring Boot PDF Extraction Service"
gh repo create derai-react-ui --private --description "DERAI - React Dashboard"
```

### Step 2: Initial Push
```bash
# FastAPI
cd "DERAI/FastAPI services"
git init && git add . && git commit -m "feat: initial FastAPI service with extraction pipeline"
git remote add origin https://github.com/<username>/derai-fastapi.git
git push -u origin main

# Repeat for Spring Boot and React UI
```

### Step 3: Branch Protection
```
main → protected (require PR, require CI pass, require 1 review)
develop → integration branch
feature/* → short-lived feature branches
release/* → release candidates
```

## GitHub Actions Workflows

### derai-fastapi/.github/workflows/ci.yml
```yaml
name: FastAPI CI
on:
  push: { branches: [main, develop] }
  pull_request: { branches: [main] }

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest tests/ -v --tb=short
      - run: docker build -t derai-fastapi .

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install safety && safety check -r requirements.txt
```

### GitHub Agent Workflow (Copilot Agent for PR Validation)

```yaml
name: Copilot Agent Validation
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Build and start services
      - name: Start services
        run: docker compose up -d --build
        working-directory: .
      
      # Wait for health
      - name: Wait for FastAPI
        run: |
          for i in {1..30}; do
            curl -sf http://localhost:8000/health && break
            sleep 2
          done
      
      # Run validation use case
      - name: Validate document processing
        run: |
          # Process a sample statement document
          RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/process-single \
            -H "Content-Type: application/json" \
            -H "X-API-Key: derai-dev-key-2026" \
            -d '{
              "account": {"office": "001", "account_number": "123456"},
              "document_type": "statement",
              "extraction_engine": "pymupdf"
            }')
          
          echo "Response: $RESPONSE"
          
          # Verify response has expected fields
          echo "$RESPONSE" | python3 -c "
          import json, sys
          r = json.load(sys.stdin)
          assert r.get('success') is True, 'Processing should succeed'
          assert r.get('comparison'), 'Should have comparison results'
          print('✅ Document verification use case PASSED')
          "
      
      - name: Cleanup
        if: always()
        run: docker compose down
```

## Branching Strategy

```
main ──────────────────────────────────────────────── (production)
  │
  └── develop ─────────────────────────────────────── (integration)
        │
        ├── feature/add-azure-ocr ──────── PR → develop
        │
        ├── feature/batch-processing ───── PR → develop
        │
        └── feature/redis-caching ──────── PR → develop

Release Flow:
  develop → release/1.0.0 → (testing) → PR → main → tag v1.0.0
```

## Repository README Template

Each repo should have:
1. **Badges**: CI status, coverage, Python/Java version
2. **Quick start**: 3 commands to run locally
3. **Architecture**: Link to derai-docs
4. **API docs**: Auto-generated Swagger link
5. **Contributing**: PR process, code standards
6. **License**: MIT or internal

## Migration Plan (Monorepo → 3 Repos)

```bash
# 1. Split FastAPI service
git filter-repo --subdirectory-filter "FastAPI services" --force
git remote add origin https://github.com/<username>/derai-fastapi.git
git push

# 2. Split Spring Boot service
git filter-repo --subdirectory-filter "Springboot services" --force
git remote add origin https://github.com/<username>/derai-springboot.git
git push

# 3. Split React UI
git filter-repo --subdirectory-filter "React UI" --force
git remote add origin https://github.com/<username>/derai-react-ui.git
git push
```
