#!/bin/bash

# ===========================================
# Todo App Status Check Script
# ===========================================
# This script shows the status of your Todo application
#
# Usage: ./status-app.sh
# ===========================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   Todo App Status Check                ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check Docker
echo -e "${YELLOW}[Docker Status]${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}Docker: Running${NC}"
else
    echo -e "${RED}Docker: Not Running${NC}"
fi
echo ""

# Check Minikube
echo -e "${YELLOW}[Minikube Status]${NC}"
minikube status 2>/dev/null || echo -e "${RED}Minikube: Not Running${NC}"
echo ""

# Check Pods
echo -e "${YELLOW}[Pod Status]${NC}"
kubectl get pods 2>/dev/null || echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
echo ""

# Check Services
echo -e "${YELLOW}[Service Status]${NC}"
kubectl get svc 2>/dev/null || echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
echo ""

# Show app URL if running
echo -e "${YELLOW}[Application URL]${NC}"
MINIKUBE_STATUS=$(minikube status --format='{{.Host}}' 2>/dev/null || echo "Stopped")
if [ "$MINIKUBE_STATUS" == "Running" ]; then
    echo "To open the app, run: minikube service todo-frontend"
else
    echo "App is not running. Start with: ./start-app.sh"
fi
echo ""
