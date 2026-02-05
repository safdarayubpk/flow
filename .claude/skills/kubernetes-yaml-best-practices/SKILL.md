---
name: kubernetes-yaml-best-practices
description: |
  Generate production-ready Kubernetes YAML manifests following best practices. Use when creating or reviewing: Deployments, Services, ConfigMaps, Secrets, Ingress, PersistentVolumeClaims, or any k8s resource YAML. Triggers: "kubernetes manifest", "deployment yaml", "service yaml", "write k8s resource", "create kubernetes", "k8s yaml", "pod spec", "container spec". NOT for Helm charts, Kustomize overlays, or kubectl commands.
---

# Kubernetes YAML Best Practices

Generate valid, production-ready Kubernetes manifests.

## API Versions

Use stable APIs:
- `v1`: Pod, Service, ConfigMap, Secret, PersistentVolumeClaim, Namespace
- `apps/v1`: Deployment, StatefulSet, DaemonSet, ReplicaSet
- `networking.k8s.io/v1`: Ingress, NetworkPolicy
- `batch/v1`: Job, CronJob

## Required Labels

Always include standard labels:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: <app-name>
    app.kubernetes.io/instance: <instance-id>
    app.kubernetes.io/component: <component>  # frontend, backend, database
```

## Deployment Pattern (Prefer Over Pod)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <app>-deployment
  labels:
    app.kubernetes.io/name: <app>
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: <app>
  template:
    metadata:
      labels:
        app.kubernetes.io/name: <app>
    spec:
      containers:
        - name: <app>
          image: <image>:<tag>  # Always specify tag, never :latest in prod
          ports:
            - containerPort: 8080
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
      restartPolicy: Always  # Default for Deployments
```

## Service Pattern

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <app>-service
  labels:
    app.kubernetes.io/name: <app>
spec:
  type: ClusterIP  # Or LoadBalancer, NodePort
  selector:
    app.kubernetes.io/name: <app>  # Must match pod labels
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
```

## Resource Requirements

Always specify for production:

```yaml
resources:
  requests:   # Scheduling guarantee
    memory: "128Mi"
    cpu: "100m"
  limits:     # Hard cap
    memory: "256Mi"
    cpu: "500m"
```

## Health Probes

Add probes for any long-running container:

| Probe | Purpose | When |
|-------|---------|------|
| `readinessProbe` | Traffic routing | Always for services |
| `livenessProbe` | Container restart | Detect deadlocks |
| `startupProbe` | Slow startup apps | Long init times |

Probe types: `httpGet`, `tcpSocket`, `exec`

## Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
```

## ConfigMap/Secret References

```yaml
env:
  - name: DB_HOST
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: database_host
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: app-secrets
        key: db_password
```

## Output Format

- Use `---` separator between multiple resources
- Add brief comments for non-obvious configurations
- Order: Namespace > ConfigMap/Secret > PVC > Deployment > Service > Ingress
