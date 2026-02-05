#!/bin/bash
# deploy.sh - Deploy Todo application to Minikube using Helm
#
# This script deploys both the backend and frontend services to Kubernetes
# using Helm charts. It also creates the required Kubernetes secret for
# sensitive configuration values.
#
# Usage:
#   ./k8s/scripts/deploy.sh
#
# Prerequisites:
#   - Minikube is running
#   - Images are loaded (./k8s/scripts/load-images.sh)
#   - kubectl is configured for Minikube
#   - Helm is installed

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo -e "${YELLOW}☸️  Deploying Todo application to Minikube...${NC}"
echo "Repository root: $REPO_ROOT"
echo ""

# Check if Minikube is running
if ! minikube status > /dev/null 2>&1; then
  echo -e "${RED}❌ Minikube is not running!${NC}"
  echo "Start Minikube with: minikube start --driver=docker"
  exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# Check if secret exists, if not remind user to create it
if ! kubectl get secret todo-secrets > /dev/null 2>&1; then
  echo -e "${YELLOW}⚠️  Secret 'todo-secrets' not found.${NC}"
  echo ""
  echo "Please create it with your actual values:"
  echo -e "${BLUE}kubectl create secret generic todo-secrets \\
  --from-literal=DATABASE_URL='your-neon-database-url' \\
  --from-literal=JWT_SECRET='your-jwt-secret' \\
  --from-literal=BETTER_AUTH_SECRET='your-better-auth-secret' \\
  --from-literal=OPENAI_API_KEY='your-openai-api-key'${NC}"
  echo ""
  echo "Then run this script again."
  exit 1
fi

echo -e "${GREEN}✓ Secret 'todo-secrets' exists${NC}"
echo ""

# Deploy backend
echo -e "${YELLOW}📦 Deploying backend...${NC}"
if helm list | grep -q todo-backend; then
  echo "Upgrading existing backend deployment..."
  helm upgrade todo-backend "$REPO_ROOT/k8s/backend"
else
  echo "Installing new backend deployment..."
  helm install todo-backend "$REPO_ROOT/k8s/backend"
fi

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Backend deployed successfully${NC}"
else
  echo -e "${RED}❌ Backend deployment failed${NC}"
  exit 1
fi

echo ""

# Deploy frontend
echo -e "${YELLOW}📦 Deploying frontend...${NC}"
if helm list | grep -q todo-frontend; then
  echo "Upgrading existing frontend deployment..."
  helm upgrade todo-frontend "$REPO_ROOT/k8s/frontend"
else
  echo "Installing new frontend deployment..."
  helm install todo-frontend "$REPO_ROOT/k8s/frontend"
fi

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Frontend deployed successfully${NC}"
else
  echo -e "${RED}❌ Frontend deployment failed${NC}"
  exit 1
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""

# Show deployment status
echo -e "${YELLOW}📊 Deployment Status:${NC}"
kubectl get pods
echo ""
kubectl get services
echo ""

# Wait for pods to be ready
echo -e "${YELLOW}⏳ Waiting for pods to be ready (this may take a minute)...${NC}"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-backend --timeout=120s 2>/dev/null || echo "Backend pod not ready yet"
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-frontend --timeout=120s 2>/dev/null || echo "Frontend pod not ready yet"
echo ""

echo -e "${GREEN}🚀 Access the application:${NC}"
echo ""
echo "Option 1 - Using minikube service (opens browser automatically):"
echo "  minikube service todo-frontend-service"
echo ""
echo "Option 2 - Using port-forward:"
echo "  kubectl port-forward svc/todo-frontend-service 3000:80"
echo "  Then open http://localhost:3000 in your browser"
echo ""
echo -e "${YELLOW}📋 Useful commands:${NC}"
echo "  kubectl get pods          # Check pod status"
echo "  kubectl logs -l app.kubernetes.io/name=todo-backend    # Backend logs"
echo "  kubectl logs -l app.kubernetes.io/name=todo-frontend   # Frontend logs"
echo "  helm uninstall todo-backend todo-frontend              # Remove deployment"
