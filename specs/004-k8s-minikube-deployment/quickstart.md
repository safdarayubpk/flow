# Quickstart: Deploy Todo App to Minikube

**Branch**: `004-k8s-minikube-deployment` | **Date**: 2026-01-27

This guide walks you through deploying the Todo app to a local Minikube Kubernetes cluster. Written for beginners learning Kubernetes for the first time.

---

## Prerequisites (Already Satisfied)

- ✅ Docker Desktop is running
- ✅ Minikube v1.37.0 installed and working
- ✅ kubectl v1.35.x connected to Minikube
- ✅ Helm v4.1.0 installed
- ✅ kubectl-ai installed (optional, for learning)

---

## Step 1: Verify Minikube is Running

```bash
# Check Minikube status
minikube status

# If not running, start it (usually already running)
# minikube start --driver=docker
```

You should see:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

## Step 2: Build Docker Images

Build the container images for both frontend and backend:

```bash
# Build backend image for Kubernetes
docker build -t todo-backend:k8s -f backend/Dockerfile.k8s ./backend

# Build frontend image for Kubernetes
docker build -t todo-frontend:k8s -f frontend/Dockerfile.k8s ./frontend
```

**What's happening**: Docker creates container images that package your app with all its dependencies.

---

## Step 3: Load Images into Minikube

Minikube has its own Docker registry. Load your images into it:

```bash
# Load backend image
minikube image load todo-backend:k8s

# Load frontend image
minikube image load todo-frontend:k8s

# Verify images are loaded
minikube image ls | grep todo
```

**What's happening**: Minikube can't pull from your local Docker. We "load" images directly into Minikube's registry.

---

## Step 4: Create Kubernetes Secret

Create a Secret with your sensitive configuration:

```bash
# Create secret from your .env file values
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='your-neon-database-url' \
  --from-literal=JWT_SECRET='your-jwt-secret' \
  --from-literal=BETTER_AUTH_SECRET='your-better-auth-secret' \
  --from-literal=OPENAI_API_KEY='your-openai-api-key'
```

**What's happening**: Secrets store sensitive data like passwords and API keys securely in Kubernetes.

---

## Step 5: Deploy Backend with Helm

```bash
# Deploy backend Helm chart
helm install todo-backend ./k8s/backend

# Watch pods start up
kubectl get pods -w

# Press Ctrl+C when pod shows "Running" and "1/1 Ready"
```

**What's happening**: Helm deploys your backend app with all its configuration (Deployment, Service, ConfigMap).

---

## Step 6: Deploy Frontend with Helm

```bash
# Deploy frontend Helm chart
helm install todo-frontend ./k8s/frontend

# Watch pods start up
kubectl get pods -w

# Press Ctrl+C when pod shows "Running" and "1/1 Ready"
```

**What's happening**: Frontend is deployed and configured to talk to backend via Kubernetes service name.

---

## Step 7: Access the Application

### Option A: Using minikube service (Recommended)

```bash
# Opens browser automatically
minikube service todo-frontend-service
```

### Option B: Using port-forward

```bash
# Forward frontend port
kubectl port-forward svc/todo-frontend-service 3000:80

# Then open http://localhost:3000 in your browser
```

---

## Step 8: Verify Everything Works

1. **Login**: Use your existing credentials or sign up
2. **AI Chatbot**: Try "Add a task to buy groceries"
3. **Task Management**: Add, complete, and delete tasks
4. **Check logs** (if issues):
   ```bash
   kubectl logs -l app.kubernetes.io/name=todo-backend
   kubectl logs -l app.kubernetes.io/name=todo-frontend
   ```

---

## Useful Commands

### Check Status

```bash
# See all resources
kubectl get all

# See pods
kubectl get pods

# See services
kubectl get svc

# See detailed pod info
kubectl describe pod <pod-name>
```

### View Logs

```bash
# Backend logs
kubectl logs -l app.kubernetes.io/name=todo-backend -f

# Frontend logs
kubectl logs -l app.kubernetes.io/name=todo-frontend -f
```

### Debug Issues

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get cluster IP
minikube ip

# Shell into a pod
kubectl exec -it <pod-name> -- /bin/sh
```

### Clean Up

```bash
# Remove deployments
helm uninstall todo-frontend
helm uninstall todo-backend

# Delete secret
kubectl delete secret todo-secrets
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ImagePullBackOff` | Run `minikube image load <image>` again |
| `CrashLoopBackOff` | Check logs: `kubectl logs <pod> --previous` |
| `Pending` | Check resources: `kubectl describe pod <pod>` |
| Connection refused | Verify service: `kubectl get svc` |

---

## Learning with kubectl-ai

Use kubectl-ai to understand Kubernetes concepts:

```bash
# Explain a deployment
kubectl-ai "explain this deployment" < k8s/backend/templates/deployment.yaml

# Debug a failing pod
kubectl-ai "why is my pod crashing"

# Learn about services
kubectl-ai "what does a ClusterIP service do"
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Minikube Cluster                         │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │  todo-frontend  │         │  todo-backend   │           │
│  │    Deployment   │         │   Deployment    │           │
│  │    (Next.js)    │         │   (FastAPI)     │           │
│  └────────┬────────┘         └────────┬────────┘           │
│           │                           │                     │
│  ┌────────▼────────┐         ┌────────▼────────┐           │
│  │ frontend-service│  ──────▶│ backend-service │           │
│  │   (ClusterIP)   │   DNS   │   (ClusterIP)   │           │
│  └────────┬────────┘         └─────────────────┘           │
│           │                                                 │
└───────────┼─────────────────────────────────────────────────┘
            │ port-forward / minikube service
            ▼
    ┌───────────────┐         ┌─────────────────┐
    │  Your Browser │         │  Neon PostgreSQL │
    │ localhost:3000│         │    (External)    │
    └───────────────┘         └─────────────────┘
```

---

**Next Steps**: After completing this deployment, you can explore:
- Scaling replicas: `kubectl scale deployment todo-backend --replicas=3`
- Viewing metrics: `kubectl top pods`
- Adding health checks monitoring
