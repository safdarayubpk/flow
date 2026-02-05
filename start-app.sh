#!/bin/bash

# ===========================================
# Todo App Kubernetes Startup Script
# ===========================================
# This script starts your Todo application on Minikube
#
# Usage: ./start-app.sh
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="/home/safdarayub/Desktop/claude/Hackathon/flow"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   Todo App Kubernetes Startup Script   ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Step 1: Check if Docker is running
echo -e "${YELLOW}[Step 1/6]${NC} Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running!${NC}"
    echo "Please start Docker Desktop first, then run this script again."
    exit 1
fi
echo -e "${GREEN}Docker is running${NC}"
echo ""

# Step 2: Start Minikube
echo -e "${YELLOW}[Step 2/6]${NC} Starting Minikube..."
MINIKUBE_STATUS=$(minikube status --format='{{.Host}}' 2>/dev/null || echo "Stopped")

if [ "$MINIKUBE_STATUS" != "Running" ]; then
    echo "Minikube is not running. Starting it now..."
    minikube start --driver=docker
else
    echo -e "${GREEN}Minikube is already running${NC}"
fi
echo ""

# Step 3: Set Docker environment to Minikube
echo -e "${YELLOW}[Step 3/6]${NC} Configuring Docker environment..."
eval $(minikube docker-env)
echo -e "${GREEN}Docker environment configured${NC}"
echo ""

# Step 4: Check if images exist, build if needed
echo -e "${YELLOW}[Step 4/6]${NC} Checking Docker images..."

BACKEND_IMAGE=$(docker images -q todo-backend:k8s 2>/dev/null)
FRONTEND_IMAGE=$(docker images -q todo-frontend:k8s 2>/dev/null)

if [ -z "$BACKEND_IMAGE" ]; then
    echo "Building backend image..."
    cd "$PROJECT_DIR"
    docker build -f backend/Dockerfile.k8s -t todo-backend:k8s backend/
    echo -e "${GREEN}Backend image built${NC}"
else
    echo -e "${GREEN}Backend image exists${NC}"
fi

if [ -z "$FRONTEND_IMAGE" ]; then
    echo "Building frontend image (this may take a few minutes)..."
    cd "$PROJECT_DIR"
    docker build -f frontend/Dockerfile.k8s -t todo-frontend:k8s frontend/
    echo -e "${GREEN}Frontend image built${NC}"
else
    echo -e "${GREEN}Frontend image exists${NC}"
fi
echo ""

# Step 5: Check pod status
echo -e "${YELLOW}[Step 5/6]${NC} Checking pod status..."

# Get pod status
BACKEND_STATUS=$(kubectl get pods -l app.kubernetes.io/name=todo-backend -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")
FRONTEND_STATUS=$(kubectl get pods -l app.kubernetes.io/name=todo-frontend -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "NotFound")

# Restart pods if they're not running properly
if [ "$BACKEND_STATUS" != "Running" ]; then
    echo "Backend pod is not running ($BACKEND_STATUS). Restarting..."
    kubectl rollout restart deployment/todo-backend 2>/dev/null || true
fi

if [ "$FRONTEND_STATUS" != "Running" ]; then
    echo "Frontend pod is not running ($FRONTEND_STATUS). Restarting..."
    kubectl rollout restart deployment/todo-frontend 2>/dev/null || true
fi

# Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-backend --timeout=120s 2>/dev/null || true
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-frontend --timeout=120s 2>/dev/null || true

echo ""
echo -e "${GREEN}Pod Status:${NC}"
kubectl get pods
echo ""

# Step 6: Open the application
echo -e "${YELLOW}[Step 6/6]${NC} Opening the application..."
echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   Application is starting!             ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "The browser will open automatically."
echo "If not, check the URL shown below."
echo ""
echo -e "${YELLOW}NOTE: Keep this terminal open while using the app!${NC}"
echo ""

# Open the service
minikube service todo-frontend
