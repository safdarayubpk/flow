---
name: k8s-security-basics
description: |
  Apply Kubernetes pod security hardening with securityContext, Pod Security Standards, and container isolation. Use for: adding runAsNonRoot, readOnlyRootFilesystem, dropping capabilities, seccomp profiles, and privilege escalation prevention. Triggers: "secure pod", "pod security", "non-root container", "security context", "k8s security", "harden deployment", "pod security standards", "restricted PSS". NOT for: NetworkPolicies, RBAC, Secrets management, or service mesh security. Use alongside kubernetes-yaml-best-practices for complete manifests.
---

# Kubernetes Security Basics

Apply security hardening to pods and containers.

## Mandatory Security Context

**Always include both pod-level and container-level securityContext:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      # Pod-level security context
      securityContext:
        runAsNonRoot: true       # Prevent root user
        runAsUser: 1000          # Run as unprivileged user
        runAsGroup: 1000         # Primary group
        fsGroup: 1000            # Volume ownership
        seccompProfile:
          type: RuntimeDefault   # Enable default seccomp filtering
      containers:
        - name: app
          image: app:1.0.0
          # Container-level security context
          securityContext:
            allowPrivilegeEscalation: false  # Block privilege escalation
            readOnlyRootFilesystem: true     # Immutable container filesystem
            capabilities:
              drop:
                - ALL                        # Drop all Linux capabilities
```

## Security Settings Explained

| Setting | Level | Purpose |
|---------|-------|---------|
| `runAsNonRoot: true` | Pod | Blocks containers running as UID 0 |
| `runAsUser: 1000` | Pod | Sets explicit non-root UID |
| `runAsGroup: 1000` | Pod | Sets primary GID |
| `fsGroup: 1000` | Pod | Sets volume file ownership |
| `allowPrivilegeEscalation: false` | Container | Prevents setuid/setgid exploits |
| `readOnlyRootFilesystem: true` | Container | Blocks filesystem writes (use emptyDir for writable paths) |
| `capabilities.drop: ["ALL"]` | Container | Removes all Linux capabilities |
| `seccompProfile.type: RuntimeDefault` | Pod | Applies container runtime's default syscall filter |

## Pod Security Standards

Target the **restricted** profile (most secure):

| Profile | Use Case |
|---------|----------|
| `privileged` | System-level workloads only (avoid) |
| `baseline` | Minimally restricted, blocks known exploits |
| `restricted` | Hardened, production default |

## Writable Paths Pattern

When `readOnlyRootFilesystem: true`, mount emptyDir for required writable paths:

```yaml
spec:
  containers:
    - name: app
      securityContext:
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: cache
          mountPath: /app/.cache
  volumes:
    - name: tmp
      emptyDir: {}
    - name: cache
      emptyDir: {}
```

## Complete Secure Container Template

```yaml
containers:
  - name: app
    image: app:1.0.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
          - ALL
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
```

## Security Checklist

Before generating any pod/deployment YAML, verify:

- [ ] `runAsNonRoot: true` at pod level
- [ ] `runAsUser/runAsGroup/fsGroup` set to non-zero (e.g., 1000)
- [ ] `allowPrivilegeEscalation: false` on each container
- [ ] `readOnlyRootFilesystem: true` with emptyDir for writable paths
- [ ] `capabilities.drop: ["ALL"]` on each container
- [ ] `seccompProfile.type: RuntimeDefault` at pod level

**If any setting is missing, add it with a comment explaining its purpose.**
