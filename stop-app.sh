#!/bin/bash

# ===========================================
# Todo App Kubernetes Stop Script
# ===========================================
# This script stops your Todo application
#
# Usage: ./stop-app.sh
# ===========================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   Todo App Kubernetes Stop Script      ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

echo -e "${YELLOW}Stopping Minikube...${NC}"
minikube stop

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}   Application stopped successfully!    ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "To start again, run: ./start-app.sh"
echo ""
