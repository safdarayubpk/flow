# Quickstart: OCI OKE Cloud Deployment

**Feature**: 008-oci-oke-cloud-deployment
**Cluster**: todo-oke-cluster (me-dubai-1)
**Node**: 1x VM.Standard.E2.1 (1 OCPU, 8GB RAM, x86)

## Prerequisites

- OCI CLI authenticated with MFA session: `oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION`
- kubectl configured via `~/.oci/oke-token.sh` wrapper (v1beta1→v1 conversion)
- Helm v4.1.0+ installed
- Docker images pushed: `safdarayub/todo-backend:v3-complete`, `safdarayub/todo-frontend:v3-complete`

## Quick Deploy (all commands)

```bash
# 0. Verify access
kubectl get nodes

# 1. Helm repos
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update

# 2. NGINX Ingress with OCI LB
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.annotations."oci\.oraclecloud\.com/load-balancer-type"="lb" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape"="flexible" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-min"="10" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/oci-load-balancer-shape-flex-max"="10" \
  --set controller.service.annotations."oci-network-load-balancer\.oraclecloud\.com/subnet"="ocid1.subnet.oc1.me-dubai-1.aaaaaaaasbvbt52uox37vywgrqmv3pawnznopr43syql5z6qviepthuk7qua" \
  --set controller.resources.requests.cpu=50m \
  --set controller.resources.requests.memory=64Mi \
  --set controller.resources.limits.cpu=200m \
  --set controller.resources.limits.memory=128Mi \
  --set controller.admissionWebhooks.enabled=false

# 3. Wait for LB IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -w
# Ctrl+C when IP appears, then:
export LB_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "LB IP: $LB_IP"

# 4. Dapr
helm install dapr dapr/dapr \
  --namespace dapr-system --create-namespace \
  --set global.logAsJson=true \
  --set dapr_sidecar_injector.resources.requests.cpu=10m \
  --set dapr_sidecar_injector.resources.requests.memory=32Mi \
  --set dapr_sidecar_injector.resources.limits.cpu=100m \
  --set dapr_sidecar_injector.resources.limits.memory=64Mi \
  --set dapr_operator.resources.requests.cpu=10m \
  --set dapr_operator.resources.requests.memory=32Mi \
  --set dapr_operator.resources.limits.cpu=100m \
  --set dapr_operator.resources.limits.memory=64Mi \
  --set dapr_placement.resources.requests.cpu=10m \
  --set dapr_placement.resources.requests.memory=32Mi \
  --set dapr_placement.resources.limits.cpu=100m \
  --set dapr_placement.resources.limits.memory=64Mi \
  --set dapr_sentry.resources.requests.cpu=10m \
  --set dapr_sentry.resources.requests.memory=32Mi \
  --set dapr_sentry.resources.limits.cpu=100m \
  --set dapr_sentry.resources.limits.memory=64Mi

# 5. Kafka (KRaft mode, no Zookeeper needed)
kubectl apply -f k8s/kafka.yaml
kubectl wait --for=condition=ready pod -l app=kafka --timeout=120s

# 6. Dapr component
kubectl apply -f k8s/dapr-kafka-pubsub.yaml

# 7. Secrets (replace placeholders with real values)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL='<YOUR_NEON_DATABASE_URL>' \
  --from-literal=SECRET_KEY='<YOUR_SECRET_KEY>' \
  --from-literal=BETTER_AUTH_SECRET='<YOUR_BETTER_AUTH_SECRET>' \
  --from-literal=GROQ_API_KEY='<YOUR_GROQ_API_KEY>' \
  --from-literal=OPENAI_API_KEY='<YOUR_OPENAI_API_KEY>'

# 8. Update LB_IP in values-oci.yaml files
sed -i "s/<LB_IP>/$LB_IP/g" k8s/backend/values-oci.yaml
sed -i "s/<LB_IP>/$LB_IP/g" k8s/frontend/values-oci.yaml

# 9. Backend
helm upgrade --install todo-backend ./k8s/backend --values k8s/backend/values-oci.yaml

# 10. Frontend
helm upgrade --install todo-frontend ./k8s/frontend --values k8s/frontend/values-oci.yaml

# 11. Ingress
kubectl apply -f k8s/ingress.yaml

# 12. Verify
kubectl get pods
kubectl get svc
kubectl get ingress
curl -s http://$LB_IP/api/v1/auth/session  # Backend API responds
curl -s http://$LB_IP | head -5             # Frontend loads
```

## Quick Teardown

```bash
kubectl delete ingress todo-ingress-api todo-ingress-frontend 2>/dev/null
helm uninstall todo-frontend 2>/dev/null
helm uninstall todo-backend 2>/dev/null
kubectl delete secret todo-secrets 2>/dev/null
kubectl delete -f k8s/dapr-kafka-pubsub.yaml 2>/dev/null
kubectl delete -f k8s/kafka.yaml 2>/dev/null
kubectl delete pvc kafka-data 2>/dev/null
helm uninstall dapr -n dapr-system 2>/dev/null
kubectl delete namespace dapr-system 2>/dev/null
helm uninstall ingress-nginx -n ingress-nginx 2>/dev/null
kubectl delete namespace ingress-nginx 2>/dev/null
```

## MFA Refresh

If any command returns `401 Unauthorized` or JSON decode error:

```bash
oci session authenticate --region me-dubai-1 --profile-name OKE_SESSION
```

## Known Risk

`NEXT_PUBLIC_API_URL` is a build-time Next.js variable. If client-side API calls fail (browser console shows requests to wrong URL), use relative URLs or rebuild the image:

```bash
# Option A: Frontend uses relative /api paths (works if ingress routing is correct)
# Option B: Rebuild with correct URL
docker build -t safdarayub/todo-frontend:v3-complete \
  --build-arg NEXT_PUBLIC_API_URL=http://$LB_IP/api \
  -f frontend/Dockerfile.k8s frontend/
docker push safdarayub/todo-frontend:v3-complete
kubectl rollout restart deployment todo-frontend
```
