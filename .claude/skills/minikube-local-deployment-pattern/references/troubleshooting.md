# Minikube Troubleshooting Guide

## Table of Contents
- [ImagePullBackOff](#imagepullbackoff)
- [CrashLoopBackOff](#crashloopbackoff)
- [Readiness/Liveness Probe Failures](#readinessliveness-probe-failures)
- [Pending Pods](#pending-pods)
- [Service Not Accessible](#service-not-accessible)
- [Resource Issues](#resource-issues)

---

## ImagePullBackOff

**Symptoms:** Pod stuck in `ImagePullBackOff` or `ErrImagePull`

**Diagnosis:**
```bash
kubectl describe pod <pod-name> | grep -A5 "Events:"
```

**Common causes and fixes:**

### Cause 1: Local image not loaded
```bash
# Check if image exists in minikube
minikube image ls | grep <image-name>

# If not, load it
minikube image load <image>:<tag>
```

### Cause 2: Missing imagePullPolicy
```yaml
# Add to container spec
imagePullPolicy: Never  # For local images
# Or
imagePullPolicy: IfNotPresent  # For cached images
```

### Cause 3: Wrong image name/tag
```bash
# List available images
minikube image ls

# Compare with deployment
kubectl get deployment <name> -o jsonpath='{.spec.template.spec.containers[0].image}'
```

---

## CrashLoopBackOff

**Symptoms:** Pod repeatedly crashes, status shows `CrashLoopBackOff`

**Diagnosis:**
```bash
# View logs from crashed container
kubectl logs <pod-name> --previous

# Check exit code
kubectl describe pod <pod-name> | grep -A3 "Last State:"
```

**Common causes:**

### Cause 1: Application error on startup
- Check logs for stack traces
- Verify environment variables are set
- Check config file paths

### Cause 2: Missing environment variables
```bash
# Check current env vars
kubectl exec <pod-name> -- env

# Verify ConfigMap/Secret exists
kubectl get configmap
kubectl get secret
```

### Cause 3: Port already in use inside container
- Ensure container listens on correct port
- Check for conflicting processes

### Cause 4: Insufficient permissions
```bash
# Check security context
kubectl get pod <pod-name> -o jsonpath='{.spec.securityContext}'

# Try running as root temporarily for debugging
securityContext:
  runAsUser: 0
```

---

## Readiness/Liveness Probe Failures

**Symptoms:** Pod shows `0/1 Ready`, restarts frequently

**Diagnosis:**
```bash
kubectl describe pod <pod-name> | grep -A10 "Readiness:"
kubectl describe pod <pod-name> | grep -A10 "Liveness:"
```

**Common causes:**

### Cause 1: Wrong probe path
```bash
# Test endpoint from inside pod
kubectl exec <pod-name> -- curl -s localhost:8080/health
```

### Cause 2: Wrong port
```bash
# Check what ports container is listening on
kubectl exec <pod-name> -- netstat -tlnp
# Or
kubectl exec <pod-name> -- ss -tlnp
```

### Cause 3: Probe fires before app is ready
```yaml
# Increase initial delay
readinessProbe:
  initialDelaySeconds: 30  # Give app more time to start
  periodSeconds: 10
```

### Cause 4: Probe timeout too short
```yaml
livenessProbe:
  timeoutSeconds: 5  # Increase from default 1s
```

---

## Pending Pods

**Symptoms:** Pod stuck in `Pending` state

**Diagnosis:**
```bash
kubectl describe pod <pod-name> | grep -A10 "Events:"
```

**Common causes:**

### Cause 1: Insufficient resources
```bash
# Check node resources
kubectl describe node | grep -A5 "Allocated resources:"

# Reduce resource requests
resources:
  requests:
    memory: "64Mi"  # Lower values
    cpu: "50m"
```

### Cause 2: Node selector mismatch
```bash
# Check node labels
kubectl get nodes --show-labels
```

### Cause 3: PVC not bound
```bash
kubectl get pvc
kubectl describe pvc <pvc-name>
```

---

## Service Not Accessible

**Symptoms:** Cannot reach service via minikube service or port-forward

**Diagnosis:**
```bash
# Check service exists and has endpoints
kubectl get svc
kubectl get endpoints <service-name>
```

**Common causes:**

### Cause 1: Selector mismatch
```bash
# Check service selector
kubectl get svc <service-name> -o jsonpath='{.spec.selector}'

# Check pod labels
kubectl get pods --show-labels

# Labels must match exactly
```

### Cause 2: Wrong target port
```bash
# Service targetPort must match container port
kubectl get svc <service-name> -o yaml | grep -A5 "ports:"
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].ports}'
```

### Cause 3: Pod not ready
```bash
# Endpoints only include Ready pods
kubectl get endpoints <service-name>
# Empty ENDPOINTS = no ready pods
```

---

## Resource Issues

### Check minikube resources
```bash
minikube config view
minikube ssh -- free -m
minikube ssh -- df -h
```

### Increase minikube resources
```bash
# Stop minikube first
minikube stop

# Reconfigure (requires cluster recreation)
minikube config set memory 4096
minikube config set cpus 2
minikube delete
minikube start
```

### Clean up resources
```bash
# Remove unused images
minikube image rm <image>

# Prune docker inside minikube
minikube ssh -- docker system prune -af
```
