# Dapr Component Contracts

## kafka-pubsub Component

**File**: `backend/components/kafka-pubsub.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: consumerGroup
    value: "dapr-todo-backend"
  - name: authRequired
    value: "false"
  - name: maxMessageBytes
    value: "1048576"
```

## Dapr Run Configuration

```bash
dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --app-protocol http \
  --resources-path ./backend/components \
  -- uvicorn backend.backend.src.main:app --host 0.0.0.0 --port 8000
```

**Ports**:
- `8000`: FastAPI app (existing)
- `3500`: Dapr sidecar HTTP API (new)
- `50001`: Dapr sidecar gRPC (new, auto)
- `9092`: Kafka broker (existing)
- `8080`: Kafka UI (existing)