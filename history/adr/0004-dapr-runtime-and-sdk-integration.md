# ADR-0004: Dapr Runtime and SDK Integration

> **Scope**: Dapr runtime mode, Python SDK selection, and FastAPI integration pattern for event-driven microservices.

- **Status:** Accepted
- **Date:** 2026-02-15
- **Feature:** 007-dapr-microservices
- **Context:** The Todo application needs to evolve from direct Kafka client usage (aiokafka) to a broker-agnostic event-driven architecture. Dapr provides runtime abstractions for pub/sub, service invocation, and other building blocks. The decision involves which Dapr runtime mode to use, which Python packages to adopt, and how to integrate Dapr with the existing FastAPI application.

## Decision

We will adopt the following Dapr integration stack:

- **Runtime Mode**: Dapr self-hosted (local mode via `dapr run`, no Kubernetes)
- **Core SDK**: `dapr` Python package (provides `DaprClient` for publishing and service invocation)
- **FastAPI Extension**: `dapr-ext-fastapi` (provides `DaprApp` wrapper with `@dapr_app.subscribe()` decorator)
- **Integration Pattern**: `DaprApp(app)` wraps the existing FastAPI app; subscriptions registered as decorated handler functions
- **Sidecar Configuration**: `dapr run --app-id todo-backend --app-port 8000 --resources-path ./backend/components`
- **Component Directory**: `backend/components/` stores Dapr YAML component configs

## Consequences

### Positive

- Broker-agnostic: switching from Kafka to Redis/RabbitMQ/etc. requires only a component YAML change, no code change
- `dapr-ext-fastapi` provides idiomatic FastAPI integration via decorators (beginner-friendly)
- Self-hosted mode requires no Kubernetes setup — developer runs `dapr run` locally
- DaprApp wrapper is non-invasive: existing FastAPI routes, middleware, and lifespan are unchanged
- Path to Kubernetes: same code works in Kubernetes with Dapr operator in Phase V.4
- Two building blocks (pub/sub + service invocation) from same SDK

### Negative

- Adds Dapr CLI + runtime as local development prerequisite
- Sidecar process adds memory/CPU overhead alongside the FastAPI app
- `dapr-ext-fastapi` has smaller community and documentation than core Dapr SDK
- DaprClient is synchronous — requires `asyncio.to_thread()` or sync context manager in async FastAPI
- `dapr init` installs Redis and Zipkin containers by default (unused in this phase)

## Alternatives Considered

**Alternative A: Direct Dapr HTTP API (no SDK)**
- Call Dapr sidecar HTTP endpoints directly (`http://localhost:3500/v1.0/publish/...`)
- Why rejected: Loses type safety, requires manual HTTP client management, more boilerplate code

**Alternative B: Dapr gRPC SDK**
- Use `dapr` package with gRPC transport instead of HTTP
- Why rejected: Added complexity for no benefit in local dev; HTTP is simpler to debug and sufficient for this use case

**Alternative C: Skip Dapr, use CloudEvents directly over Kafka**
- Implement CloudEvents envelope manually while keeping aiokafka
- Why rejected: Doesn't provide broker abstraction, no subscription model, doesn't meet "at least 2 Dapr building blocks" requirement

**Alternative D: Dapr on Kubernetes (skip self-hosted)**
- Deploy Dapr directly on Minikube with Kubernetes operator
- Why rejected: Out of scope for Phase V.3; self-hosted is simpler for beginners; Kubernetes deferred to V.4

## References

- Feature Spec: [specs/007-dapr-microservices/spec.md](../../specs/007-dapr-microservices/spec.md)
- Implementation Plan: [specs/007-dapr-microservices/plan.md](../../specs/007-dapr-microservices/plan.md)
- Research: [specs/007-dapr-microservices/research.md](../../specs/007-dapr-microservices/research.md) (R1, R2, R6)
- Related ADRs: [ADR-0001](./0001-kafka-infrastructure-stack.md) (Kafka infrastructure reused as Dapr backend)