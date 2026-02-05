# Dockerfile Specifications for Kubernetes

**Branch**: `004-k8s-minikube-deployment` | **Date**: 2026-01-27

This document specifies the Dockerfiles needed for Kubernetes deployment.

---

## Backend Dockerfile (Dockerfile.k8s)

**Location**: `backend/Dockerfile.k8s`
**Base Image**: `python:3.13-slim`
**Port**: 8000

### Requirements

1. **Multi-stage build**: Use build stage for dependencies, slim runtime stage
2. **Non-root user**: Create and use user with UID 1000
3. **Working directory**: `/app`
4. **Dependencies**: Install via UV package manager
5. **Health check**: Expose `/health` endpoint
6. **Entry point**: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### Key Differences from Hugging Face Dockerfile

| Aspect | Hugging Face (existing) | Kubernetes (new) |
|--------|-------------------------|------------------|
| Port | 7860 | 8000 |
| User | Hugging Face specific | UID 1000 |
| File | Dockerfile | Dockerfile.k8s |

### Specification

```dockerfile
# Stage 1: Build dependencies
FROM python:3.13-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

# Stage 2: Runtime
FROM python:3.13-slim AS runtime
WORKDIR /app

# Create non-root user (UID 1000 for Kubernetes security context)
RUN useradd -m -u 1000 appuser

# Copy dependencies from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY src/ ./src/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Frontend Dockerfile (Dockerfile.k8s)

**Location**: `frontend/Dockerfile.k8s`
**Base Image**: `node:20-alpine`
**Port**: 3000

### Requirements

1. **Multi-stage build**: Build stage for Next.js, slim runtime stage
2. **Non-root user**: Use node user (UID 1000)
3. **Working directory**: `/app`
4. **Build output**: Standalone Next.js build
5. **Health check**: Expose `/api/health` endpoint
6. **Entry point**: `node server.js` (standalone output)

### Specification

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build-time environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js application
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app

# Set runtime environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Create directories for Next.js cache (writable paths)
RUN mkdir -p /app/.next/cache /tmp && \
    chown -R node:node /app /tmp

# Copy standalone build output
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public

# Switch to non-root user
USER node

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1

# Run application
CMD ["node", "server.js"]
```

---

## Image Build Commands

```bash
# Backend
docker build -t todo-backend:k8s -f backend/Dockerfile.k8s ./backend

# Frontend
docker build -t todo-frontend:k8s -f frontend/Dockerfile.k8s ./frontend
```

## Image Load Commands (Minikube)

```bash
# Load into Minikube
minikube image load todo-backend:k8s
minikube image load todo-frontend:k8s

# Verify
minikube image ls | grep todo
```
