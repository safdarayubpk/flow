#!/bin/bash
# load-images.sh - Load Docker images into Minikube
#
# Minikube has its own Docker registry separate from your local Docker.
# This script loads locally built images into Minikube so Kubernetes
# can use them without pulling from a remote registry.
#
# Usage:
#   ./k8s/scripts/load-images.sh
#
# Prerequisites:
#   - Minikube is running (minikube status)
#   - Images are built (./k8s/scripts/build-images.sh)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Loading Docker images into Minikube...${NC}"
echo ""

# Check if Minikube is running
if ! minikube status > /dev/null 2>&1; then
  echo -e "${RED}❌ Minikube is not running!${NC}"
  echo "Start Minikube with: minikube start --driver=docker"
  exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Load backend image
echo -e "${YELLOW}📦 Loading todo-backend:k8s into Minikube...${NC}"
minikube image load todo-backend:k8s

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Backend image loaded successfully${NC}"
else
  echo -e "${RED}❌ Backend image load failed${NC}"
  exit 1
fi

echo ""

# Load frontend image
echo -e "${YELLOW}📦 Loading todo-frontend:k8s into Minikube...${NC}"
minikube image load todo-frontend:k8s

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Frontend image loaded successfully${NC}"
else
  echo -e "${RED}❌ Frontend image load failed${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}🎉 All images loaded into Minikube!${NC}"
echo ""

# Verify images are loaded
echo "Verifying images in Minikube:"
minikube image ls | grep todo || echo "No todo images found (this might be a display issue)"
echo ""
echo "Next step: Run ./k8s/scripts/deploy.sh to deploy the application"
