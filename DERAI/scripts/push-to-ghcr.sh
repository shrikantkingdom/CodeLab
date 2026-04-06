#!/bin/bash
# ──────────────────────────────────────────────────────────
# DERAI — Push Docker images to GitHub Container Registry
# ──────────────────────────────────────────────────────────
# Usage:
#   ./scripts/push-to-ghcr.sh
#
# Prerequisites:
#   export GITHUB_TOKEN=ghp_xxxxx   (PAT with write:packages scope)
#   docker login ghcr.io -u <username> --password-stdin <<< "$GITHUB_TOKEN"
# ──────────────────────────────────────────────────────────

set -euo pipefail

OWNER="shrikantkingdom"
REGISTRY="ghcr.io/${OWNER}"

SERVICES=("derai-fastapi" "derai-springboot" "derai-react-ui")

echo "═══════════════════════════════════════════════════"
echo "  DERAI — Push images to GHCR"
echo "═══════════════════════════════════════════════════"

# Check Docker login
if ! docker pull ghcr.io/library/hello-world 2>/dev/null; then
  echo ""
  echo "⚠️  Not logged in to GHCR. Run:"
  echo "   echo \$GITHUB_TOKEN | docker login ghcr.io -u ${OWNER} --password-stdin"
  echo ""
fi

# Build all images
echo ""
echo "📦 Building all images..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}/.."
docker compose build

# Tag and push
echo ""
GIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

for IMAGE in "${SERVICES[@]}"; do
  echo "🚀 Pushing ${IMAGE}..."
  docker tag "${IMAGE}:latest" "${REGISTRY}/${IMAGE}:latest"
  docker tag "${IMAGE}:latest" "${REGISTRY}/${IMAGE}:${GIT_SHA}"
  docker push "${REGISTRY}/${IMAGE}:latest"
  docker push "${REGISTRY}/${IMAGE}:${GIT_SHA}"
  echo "   ✅ ${REGISTRY}/${IMAGE}:latest"
  echo "   ✅ ${REGISTRY}/${IMAGE}:${GIT_SHA}"
  echo ""
done

echo "═══════════════════════════════════════════════════"
echo "  ✅ All images pushed to ${REGISTRY}"
echo ""
echo "  Run anywhere with:"
echo "    docker compose -f docker-compose.ghcr.yml up -d"
echo "═══════════════════════════════════════════════════"
