# DevOps & Deployment

## Docker Architecture

All 3 services run in Docker containers orchestrated by Docker Compose:

```
docker-compose.yml
├── fastapi-service (python:3.11-slim → port 8000)
├── springboot-service (temurin:17-jre → port 8080)
└── react-ui (node:20 → nginx:alpine → port 3000)
    └── nginx proxies /api → fastapi-service:8000
```

### Using Docker Compose (V2)

**Important**: Use `docker compose` (with space), not `docker-compose` (hyphenated). The legacy `docker-compose` binary is deprecated.

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d --build

# View logs
docker compose logs -f fastapi-service

# Stop
docker compose down

# Rebuild single service
docker compose build fastapi-service && docker compose up -d fastapi-service
```

### Container Details

| Service | Base Image | Size | Healthcheck |
|---------|-----------|------|-------------|
| FastAPI | python:3.11-slim | ~250MB | GET /health |
| Spring Boot | eclipse-temurin:17-jre | ~300MB | GET /health |
| React UI | nginx:1.25-alpine | ~25MB | nginx -t |

### Multi-Stage Builds
All Dockerfiles use multi-stage builds:
- **Build stage**: Full SDK/toolchain for compilation
- **Runtime stage**: Minimal image with only runtime deps
- **Non-root user**: All containers run as non-root for security

## Environment Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
```

Key variables:
```env
# API
API_KEY=derai-dev-key-2026
PDF_API_BASE_URL=https://pdf-api.internal.com

# FastAPI
OPENAI_API_KEY=sk-...

# Azure OCR (optional)
AZURE_DOC_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOC_API_KEY=your-key

# Databases (empty = mock mode)
SNOWFLAKE_ACCOUNT=
DB2_HOST=
```

## CI/CD — GitHub Actions

Three separate workflows for independent deployment:

### 1. FastAPI CI (`.github/workflows/fastapi-ci.yml`)
```yaml
Triggers: Push to main (FastAPI services/**), PRs
Steps: Checkout → Python 3.11 → Install deps → Lint (ruff) → Test (pytest)
```

### 2. Spring Boot CI (`.github/workflows/springboot-ci.yml`)
```yaml
Triggers: Push to main (Springboot services/**), PRs
Steps: Checkout → Java 17 → Maven test → Build JAR
```

### 3. React CI (`.github/workflows/react-ci.yml`)
```yaml
Triggers: Push to main (React UI/**), PRs
Steps: Checkout → Node 20 → npm install → Lint → Build → (optional: deploy)
```

## Deployment Targets

| Environment | Strategy | Notes |
|-------------|----------|-------|
| **Local** | Docker Compose | All 3 services on localhost |
| **Dev/QA** | Docker Compose on EC2/VM | Single-machine deployment |
| **Staging** | Kubernetes (EKS/AKS) | Each service = Deployment + Service |
| **Production** | Kubernetes + Helm | Horizontal scaling, rolling updates |

## Kubernetes (Future)

```yaml
# Each service gets:
apiVersion: apps/v1
kind: Deployment
  replicas: 2
  containers:
    - image: derai/fastapi:latest
      resources:
        requests: { cpu: 250m, memory: 256Mi }
        limits: { cpu: 1000m, memory: 512Mi }
---
kind: Service
  type: ClusterIP
  ports: [{ port: 8000 }]
---
kind: HorizontalPodAutoscaler
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```
