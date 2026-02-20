---
name: helm-chart-todo-app
description: |
  Generate Helm 3+ chart structure for todo/task applications. Use for: creating Chart.yaml, values.yaml, and templates/ directory with Deployment and Service manifests. Triggers: "helm chart", "helm template", "helm values", "create helm chart", "helm install", "helm upgrade", "package as helm chart". NOT for: plain Kubernetes YAML (use kubernetes-yaml-best-practices), Kustomize, or kubectl commands. NOT for: CRDs, hooks, subcharts, or advanced Helm features unless explicitly requested.
---

# Helm Chart Todo App

Generate beginner-friendly Helm 3+ charts for todo/task applications.

## Chart Structure

```
<chart-name>/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration
└── templates/
    ├── deployment.yaml # Deployment manifest
    ├── service.yaml    # Service manifest
    └── _helpers.tpl    # Template helpers (optional)
```

## Chart.yaml

```yaml
apiVersion: v2
name: todo-app
description: A Helm chart for Todo application
type: application
version: 0.1.0        # Chart version
appVersion: "1.0.0"   # Application version
```

## values.yaml

```yaml
# Number of pod replicas
replicaCount: 2

# Container image configuration
image:
  repository: todo-app
  tag: "1.0.0"
  pullPolicy: IfNotPresent  # Use "Never" for minikube local images

# Service configuration
service:
  type: ClusterIP
  port: 80
  targetPort: 8000

# Resource limits and requests
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"

# Environment variables
env:
  DATABASE_URL: ""
  LOG_LEVEL: "info"

# Health check endpoints
healthCheck:
  path: /health
  port: 8000
```

## templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
  labels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Chart.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ .Chart.Name }}
        app.kubernetes.io/instance: {{ .Release.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.targetPort }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          env:
            {{- range $key, $value := .Values.env }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          readinessProbe:
            httpGet:
              path: {{ .Values.healthCheck.path }}
              port: {{ .Values.healthCheck.port }}
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: {{ .Values.healthCheck.path }}
              port: {{ .Values.healthCheck.port }}
            initialDelaySeconds: 15
            periodSeconds: 20
```

## templates/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
  labels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  type: {{ .Values.service.type }}
  selector:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.service.targetPort }}
      protocol: TCP
```

## Common Commands

```bash
# Test chart (dry-run) - ALWAYS do this first
helm install todo-release ./todo-app --dry-run --debug

# Install chart
helm install todo-release ./todo-app

# Install with custom values
helm install todo-release ./todo-app --set replicaCount=3

# Install with values file
helm install todo-release ./todo-app -f custom-values.yaml

# Upgrade existing release
helm upgrade todo-release ./todo-app

# List releases
helm list

# Uninstall
helm uninstall todo-release
```

## Override Values Examples

**For local minikube development:**
```yaml
# local-values.yaml
image:
  repository: todo-backend
  tag: dev
  pullPolicy: Never  # Required for minikube image load
replicaCount: 1
```

**For production:**
```yaml
# prod-values.yaml
image:
  repository: myregistry.io/todo-backend
  tag: "1.2.3"
replicaCount: 3
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

## Template Syntax Quick Reference

| Syntax | Purpose |
|--------|---------|
| `{{ .Values.x }}` | Access values.yaml |
| `{{ .Release.Name }}` | Helm release name |
| `{{ .Chart.Name }}` | Chart name from Chart.yaml |
| `{{ .Release.Namespace }}` | Target namespace |
| `{{- toYaml .Values.x \| nindent N }}` | Render YAML with indentation |
| `{{ $var \| quote }}` | Quote string values |
