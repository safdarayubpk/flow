---
name: minikube-local-deployment-pattern
description: |
  Deploy and test applications on local Minikube Kubernetes cluster. Use for: loading local Docker images to Minikube, exposing services locally via port-forward or minikube service, debugging pods (logs, describe, exec), troubleshooting CrashLoopBackOff/ImagePullBackOff errors. Triggers: "deploy to minikube", "minikube image load", "port-forward", "minikube service", "debug pod", "why is pod crashing", "minikube dashboard", "local kubernetes testing". NOT for: minikube installation, minikube start/stop, cloud Kubernetes, Helm charts, or writing YAML manifests (use kubernetes-yaml-best-practices for YAML).
---

# Minikube Local Deployment Pattern

Deploy and debug applications on local Minikube cluster.

## Assumptions

- Minikube is already running (do NOT run `minikube start` unless explicitly asked)
- User has kubectl configured for minikube context

## Core Workflow

### 1. Load Local Image

Always use `minikube image load` for local Docker images:

```bash
# Build and load (preferred for local development)
docker build -t myapp:dev .
minikube image load myapp:dev

# Verify image is loaded
minikube image ls | grep myapp
```

**Important:** Set `imagePullPolicy: Never` in Deployment YAML when using local images.

### 2. Apply Manifests

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Or apply all in directory
kubectl apply -f ./k8s/
```

### 3. Expose Service Locally

**Option A: minikube service (recommended)**
```bash
# Opens browser automatically
minikube service <service-name>

# Get URL only
minikube service <service-name> --url
```

**Option B: kubectl port-forward**
```bash
# Forward service
kubectl port-forward svc/<service-name> 8080:80

# Forward specific pod
kubectl port-forward pod/<pod-name> 8080:3000
```

### 4. Verify Deployment

```bash
kubectl get pods -w              # Watch pod status
kubectl get svc                  # List services
kubectl get all                  # Overview of resources
```

## Debugging Commands

| Command | Purpose |
|---------|---------|
| `kubectl logs <pod>` | View container logs |
| `kubectl logs <pod> -f` | Stream logs |
| `kubectl logs <pod> --previous` | Logs from crashed container |
| `kubectl describe pod <pod>` | Detailed pod info + events |
| `kubectl exec -it <pod> -- /bin/sh` | Shell into container |
| `kubectl get events --sort-by=.lastTimestamp` | Recent cluster events |
| `minikube dashboard` | Open K8s dashboard UI |
| `minikube ip` | Get cluster IP |

## Quick Troubleshooting

| Status | Likely Cause | Fix |
|--------|--------------|-----|
| `ImagePullBackOff` | Image not in minikube | `minikube image load <image>` + set `imagePullPolicy: Never` |
| `CrashLoopBackOff` | App crashing on start | `kubectl logs <pod> --previous` to see crash reason |
| `Pending` | Resource constraints | `kubectl describe pod` → check Events section |
| `0/1 Ready` | Readiness probe failing | Check probe path/port matches app |

**For detailed troubleshooting scenarios:** See [references/troubleshooting.md](references/troubleshooting.md)

## Local Image Deployment Template

```yaml
# Minimal deployment for local image
spec:
  containers:
    - name: myapp
      image: myapp:dev
      imagePullPolicy: Never  # REQUIRED for minikube image load
```

## Common Patterns

**Full redeploy after code change:**
```bash
docker build -t myapp:dev . && \
minikube image load myapp:dev && \
kubectl rollout restart deployment/<deployment-name>
```

**Quick cleanup:**
```bash
kubectl delete -f ./k8s/
```
