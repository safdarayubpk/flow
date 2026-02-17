# Quickstart: Kafka Event-Driven Architecture

**Feature**: 006-kafka-events | **Date**: 2026-02-11

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ with dependencies from `backend/requirements.txt`
- Existing Todo app backend configured with `.env`

## 1. Start Kafka Infrastructure

```bash
# From repository root
docker-compose -f docker-compose.kafka.yml up -d

# Verify services are running
docker ps --format "table {{.Names}}\t{{.Status}}"
```

Expected output:
```
NAMES              STATUS
todo-kafka-ui      Up (healthy)
todo-kafka         Up (healthy)
todo-zookeeper     Up (healthy)
```

Access Kafka UI: http://localhost:8080

## 2. Install Python Dependencies

```bash
cd backend
pip install aiokafka>=0.10.0
```

## 3. Configure Environment Variables

Add to `backend/backend/.env`:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=todo-events
```

**Note**: If `KAFKA_BOOTSTRAP_SERVERS` is not set, Kafka events are disabled and the app runs normally (graceful degradation).

## 4. Start the Backend

```bash
cd backend/backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

The producer connects to Kafka during startup. Consumers start as background tasks.

## 5. Run Unit Tests

```bash
cd backend/backend
python3 -m pytest tests/test_kafka_producer.py tests/test_kafka_handlers.py -v
```

Expected: All 47 tests pass covering producer, handlers, consumer routing, and event models.

## 6. Test Event Publishing (E2E)

### Step 1: Register and login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","password_confirm":"password123","name":"Tester"}'

# Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Step 2: Check Kafka offset before

```bash
docker exec todo-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic todo-events --time -1
```

### Step 3: Create a task

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Kafka Event", "priority": "high"}'
```

### Step 4: Verify event in Kafka

```bash
# Check offset increased
docker exec todo-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 --topic todo-events --time -1

# Read the event
docker exec todo-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 --topic todo-events \
  --from-beginning --timeout-ms 5000
```

Expected event structure:
```json
{
  "event_type": "task-created",
  "timestamp": "2026-02-11T00:52:00.809141+00:00",
  "user_id": "uuid-string",
  "payload": {
    "task_id": 1,
    "title": "Test Kafka Event",
    "priority": "high",
    "tags": [],
    "due_date": null
  }
}
```

### Step 5: Test all CRUD events

```bash
# Update → task-updated event
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Complete → task-completed event
curl -X PATCH http://localhost:8000/api/v1/tasks/1/complete \
  -H "Authorization: Bearer $TOKEN"

# Delete → task-deleted event
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 7. Test Graceful Degradation

```bash
# Stop Kafka
docker stop todo-kafka

# Create task while Kafka is down — should succeed
curl -X POST http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Works Without Kafka", "priority": "low"}'

# Verify: task is created (200/201 response with task data)

# Restart Kafka
docker start todo-kafka
```

## 8. Stop Everything

```bash
# Stop Kafka infrastructure
docker-compose -f docker-compose.kafka.yml down

# Stop Backend (Ctrl+C in terminal)
```

## Troubleshooting

### Kafka Won't Start

```bash
# Check logs
docker-compose -f docker-compose.kafka.yml logs kafka

# Remove old volumes and restart
docker-compose -f docker-compose.kafka.yml down -v
docker-compose -f docker-compose.kafka.yml up -d
```

### Events Not Appearing in Kafka

1. Verify `KAFKA_BOOTSTRAP_SERVERS=localhost:9092` in `.env`
2. Check that the backend started after Kafka is healthy
3. Verify topic exists: `docker exec todo-kafka kafka-topics --list --bootstrap-server localhost:9092`

### Consumer Not Processing Events

1. Check consumer group in Kafka UI (http://localhost:8080)
2. Events without `user_id` are skipped (user isolation enforcement)
3. Events without `event_type` are skipped (malformed event handling)

## Event Types Reference

| Event | Trigger | Consumer |
|-------|---------|----------|
| `task-created` | Task created via API/UI/AI | Notification |
| `task-updated` | Task modified | - |
| `task-completed` | Task marked complete | - |
| `task-deleted` | Task soft-deleted | - |
| `reminder-triggered` | Reminder scheduler fires | Notification |
| `recurring-task-created` | Recurring task created | Recurring |
| `recurring-instance-created` | Recurring consumer creates instance | - |

## Success Criteria Checklist

- [x] SC-001: Events published within 1 second of CRUD operation
- [x] SC-002: 7 event types implemented (3+ required)
- [x] SC-003: Notification consumer logs task creation
- [x] SC-004: Recurring consumer creates instances
- [x] SC-005: Kafka starts within 60 seconds via docker-compose
- [x] SC-006: All existing REST/UI/AI functionality unchanged
- [x] SC-007: System works without Kafka (graceful degradation)
- [x] SC-008: user_id present in all events (user isolation)
- [x] SC-009: Consumers recover from malformed events
- [x] SC-010: Events not lost under normal operation
