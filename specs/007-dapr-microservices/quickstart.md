# Quickstart: Dapr Microservices & Pub/Sub

**Feature**: 007-dapr-microservices

## Prerequisites

1. Docker running (for Kafka and Dapr containers)
2. Dapr CLI installed
3. Python 3.10+ with pip
4. Existing Todo app backend with `.env` configured (DATABASE_URL, SECRET_KEY)

## One-Time Setup

### Install Dapr CLI
```bash
# Linux
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Verify
dapr --version
```

### Initialize Dapr Runtime
```bash
dapr init
# Creates: placement service, scheduler, Redis (unused), Zipkin (unused)

# Verify
dapr --version
docker ps  # Should see dapr_placement, dapr_redis, dapr_zipkin, dapr_scheduler
```

### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## Running the App

### Step 1: Start Kafka
```bash
# From the project root directory
docker compose -f docker-compose.kafka.yml up -d
# Wait for healthy: Zookeeper (2181), Kafka (9092), Kafka UI (8080)

# Verify all containers are healthy
docker ps --filter "name=todo-" --format "table {{.Names}}\t{{.Status}}"
```

### Step 2: Start FastAPI with Dapr Sidecar

**Important**: Run from `backend/backend/` directory (where `src/` is located).

```bash
cd backend/backend

dapr run \
  --app-id todo-backend \
  --app-port 8000 \
  --app-protocol http \
  --resources-path /absolute/path/to/backend/components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

> Note: `--resources-path` must be an absolute path or relative to the working directory.
> The Dapr sidecar assigns a random HTTP port (shown in startup logs as "HTTP server is running on port XXXXX").

### Step 3: Verify

Look for these lines in the startup output:
```
"GET /dapr/subscribe HTTP/1.1" 200 OK
"app is subscribed to the following topics: [[todo-events]] through pubsub=kafka-pubsub"
```

```bash
# Check app health
curl http://localhost:8000/health

# Check Dapr health via service invocation
dapr invoke --app-id todo-backend --method api/dapr/health --verb GET

# Login and get a JWT token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"your@email.com","password":"your-password"}'

# Create a task (use trailing slash!) and check Kafka UI at http://localhost:8080
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt>" \
  -d '{"title": "Test Dapr event", "description": "Should appear in Kafka UI"}'
```

## Verification Checklist

- [ ] App responds at `localhost:8000/health` with `{"status": "healthy"}`
- [ ] FastAPI docs load at `localhost:8000/docs`
- [ ] Dapr startup logs show `"GET /dapr/subscribe" 200 OK`
- [ ] Creating a task shows `"POST /api/dapr/events" 200 OK` in logs
- [ ] Events appear in Kafka UI at `http://localhost:8080` (topic: `todo-events`)
- [ ] `dapr invoke --app-id todo-backend --method api/dapr/health --verb GET` returns healthy status
- [ ] Creating a recurring task (`recurrence_rule: "FREQ=DAILY;INTERVAL=1"`) generates a recurring instance

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'src.api'` | Wrong working directory | Run from `backend/backend/` directory |
| `dapr run` fails with "app port not reachable" | FastAPI not starting | Check uvicorn command and port, verify `.env` exists |
| Events not in Kafka UI | Component misconfigured | Verify `backend/components/kafka-pubsub.yaml` broker address is `localhost:9092` |
| Subscriptions not firing | Dapr can't reach app | Ensure `--app-port 8000` matches uvicorn port |
| `"pubsub kafka-pubsub not found"` | Components not loaded | Check `--resources-path` points to `backend/components/` directory |
| `docker-compose: command not found` | Docker Compose v1 not installed | Use `docker compose` (v2 syntax, no hyphen) |
| `could not translate host name` to address | DNS/network issue with Neon DB | Retry — transient network error |
| `POST /api/v1/tasks` returns 307 redirect | Missing trailing slash | Use `POST /api/v1/tasks/` (with trailing slash) |
| `too many values to unpack` in publisher | Using `metadata` instead of `publish_metadata` | Fixed: use `publish_metadata` parameter in `DaprClient.publish_event()` |
