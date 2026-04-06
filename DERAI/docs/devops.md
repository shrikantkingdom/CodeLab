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

## 3 Ways to Run DERAI

### Option 1: Local Build (Default — `docker-compose.yml`)

Build from local source code. Best for development.

```bash
git clone https://github.com/shrikantkingdom/CodeLab.git
cd CodeLab/DERAI
cp .env.example .env   # edit with your API keys
docker compose up --build -d
```

Stop / restart:
```bash
docker compose down       # stop all
docker compose up -d      # restart (no rebuild)
docker compose up --build -d  # rebuild + restart
```

> **Note:** Containers run independently of VS Code / any IDE. Close your editor, apps keep running.

---

### Option 2: Pull Pre-Built Images from GHCR (`docker-compose.ghcr.yml`)

No build needed — pulls pre-built images from GitHub Container Registry.

**Push images (one-time or after code changes):**
```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u shrikantkingdom --password-stdin

# Build & push all 3 images
./scripts/push-to-ghcr.sh
```

**Run from anywhere (no source code needed):**
```bash
# Only need: docker-compose.ghcr.yml + .env
docker compose -f docker-compose.ghcr.yml up -d
```

**Image names:**
| Service | GHCR Image |
|---------|-----------|
| FastAPI | `ghcr.io/shrikantkingdom/derai-fastapi:latest` |
| Spring Boot | `ghcr.io/shrikantkingdom/derai-springboot:latest` |
| React UI | `ghcr.io/shrikantkingdom/derai-react-ui:latest` |

---

### Option 3: GitHub Actions CI/CD (Fully Automated)

Every push to `main` automatically builds and pushes all 3 Docker images to GHCR.

**Workflow:** `.github/workflows/derai-ci.yml`

```
Push to main → Build FastAPI ─┐
             → Build Spring Boot ─┤→ Smoke Test (health checks)
             → Build React UI ─┘
```

**What it does:**
1. Builds all 3 Docker images in parallel
2. Pushes to GHCR with `:latest` and `:sha` tags
3. Runs smoke test — starts services from GHCR images and checks health endpoints
4. On PRs — builds but does NOT push (validation only)

**Manual trigger:** Go to GitHub → Actions → "CI/CD — Build & Push to GHCR" → Run workflow

**After CI builds, run anywhere:**
```bash
docker compose -f docker-compose.ghcr.yml up -d
```

---

## CI/CD — GitHub Actions

### Workflow: `.github/workflows/derai-ci.yml`

| Job | Runs On | Triggers | Push Images? |
|-----|---------|----------|-------------|
| `build-fastapi` | ubuntu-latest | Push to main, manual | Yes (`:latest` + `:sha`) |
| `build-springboot` | ubuntu-latest | Push to main, manual | Yes |
| `build-react-ui` | ubuntu-latest | Push to main, manual | Yes |
| `smoke-test` | ubuntu-latest | After all builds | N/A — validates health |

**Path filters:** Only triggers when files under `DERAI/FastAPI services/`, `DERAI/Springboot services/`, `DERAI/React UI/`, or `DERAI/docker-compose.yml` change.

**Permissions required:** `contents: read`, `packages: write` (GITHUB_TOKEN auto-granted).

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
