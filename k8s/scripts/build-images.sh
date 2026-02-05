#!/bin/bash
# build-images.sh - Build Docker images for Kubernetes deployment
#
# This script builds both frontend and backend Docker images using
# the Dockerfile.k8s files (separate from HuggingFace deployment).
#
# Usage:
#   ./k8s/scripts/build-images.sh
#
# Prerequisites:
#   - Docker Desktop is running
#   - You are in the repository root directory

set -e  # Exit on any error

# Colors for output (makes it easier to read)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo -e "${YELLOW}🐳 Building Docker images for Kubernetes...${NC}"
echo "Repository root: $REPO_ROOT"
echo ""

# Build backend image
echo -e "${YELLOW}📦 Building backend image (todo-backend:k8s)...${NC}"
docker build \
  -t todo-backend:k8s \
  -f "$REPO_ROOT/backend/Dockerfile.k8s" \
  "$REPO_ROOT/backend"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Backend image built successfully${NC}"
else
  echo -e "${RED}❌ Backend image build failed${NC}"
  exit 1
fi

echo ""

# Build frontend image
echo -e "${YELLOW}📦 Building frontend image (todo-frontend:k8s)...${NC}"
docker build \
  -t todo-frontend:k8s \
  -f "$REPO_ROOT/frontend/Dockerfile.k8s" \
  "$REPO_ROOT/frontend"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Frontend image built successfully${NC}"
else
  echo -e "${RED}❌ Frontend image build failed${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}🎉 All images built successfully!${NC}"
echo ""
echo "Images created:"
echo "  - todo-backend:k8s"
echo "  - todo-frontend:k8s"
echo ""
echo "Next step: Run ./k8s/scripts/load-images.sh to load images into Minikube"
