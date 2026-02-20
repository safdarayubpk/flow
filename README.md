# Flow Todo - Cloud-Native Task Management App

A full-stack, event-driven task management application deployed on Oracle Cloud Kubernetes (OKE). Features AI-powered chat assistant, Dapr pub/sub with Kafka event streaming, and multi-user isolation with Better Auth.

**Live Deployments:**
- OKE (full stack): `http://139.185.51.243`
- Vercel (frontend): `https://frontend-blue-six-59.vercel.app`

## Features

- **Task Management** - Full CRUD with priority levels, tags, due dates, recurring tasks, and reminders
- **AI Chat Assistant** - Natural language task creation powered by Groq AI (e.g., "Add a task for tomorrow")
- **User Authentication** - Better Auth with JWT tokens, session management, and CSRF protection
- **Multi-User Isolation** - Strict per-user data separation; users only see their own tasks
- **Event-Driven Architecture** - Dapr sidecar publishes task events to Kafka via pub/sub
- **Cloud-Native Deployment** - Runs 24/7 on OCI OKE free-tier (1 OCPU, 8GB RAM)
- **Responsive UI** - Tailwind CSS with toast notifications

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS, Sonner |
| **Backend** | FastAPI, Python 3.13+, SQLModel, Pydantic |
| **Database** | Neon PostgreSQL (serverless), Alembic migrations |
| **Auth** | Better Auth, JWT (httpOnly cookies), CSRF tokens |
| **Events** | Dapr pub/sub, Apache Kafka 3.7 (KRaft mode) |
| **AI** | Groq API (LLM chat), OpenAI SDK |
| **Infrastructure** | OCI OKE, Helm 3, NGINX Ingress, Docker |
| **Frontend Hosting** | Vercel (alternative deployment) |

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │          OCI OKE Cluster (Dubai)         │
                    │         VM.Standard.E2.1 (Free Tier)     │
                    │                                         │
  User ──► NGINX Ingress (LoadBalancer 139.185.51.243)        │
                    │                                         │
           ┌───────┴────────┐                                 │
           │                │                                 │
     /*  ──► Frontend    /api/* ──► Backend ◄──► Dapr Sidecar │
           │  (Next.js)     │    (FastAPI)       │            │
           │                │                    ▼            │
           │                │              Kafka (KRaft)      │
           │                │              topic: todo-events │
           └────────────────┘                                 │
                    │                                         │
                    │         Neon PostgreSQL (External)       │
                    └─────────────────────────────────────────┘
```

## Quick Start (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.13+
- PostgreSQL (or Neon Serverless PostgreSQL account)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # Edit with your DATABASE_URL and secrets
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local    # Edit to match backend config
npm run dev
```

## Cloud Deployment (OCI OKE)

The app is deployed on Oracle Cloud OKE using Helm charts. Key manifests:

```
k8s/
├── backend/          # Backend Helm chart
│   ├── values.yaml          # Default values
│   └── values-oci.yaml      # OCI overrides (image, resources, env)
├── frontend/         # Frontend Helm chart
│   ├── values.yaml
│   └── values-oci.yaml
├── kafka.yaml               # Kafka StatefulSet (KRaft mode)
├── dapr-kafka-pubsub.yaml   # Dapr pub/sub component CRD
└── ingress.yaml             # NGINX Ingress routing rules
```

### Resource Budget (Free-Tier)

| Component | CPU Request | CPU Limit | RAM Request | RAM Limit |
|-----------|------------|-----------|-------------|-----------|
| Backend | 64m | 250m | 128Mi | 384Mi |
| Frontend | 64m | 250m | 128Mi | 384Mi |
| Kafka (KRaft) | 100m | 500m | 512Mi | 1Gi |
| Dapr Sidecar | 10m | 100m | 32Mi | 64Mi |
| NGINX Ingress | 50m | 200m | 64Mi | 128Mi |
| **Total** | **288m** | **1300m** | **864Mi** | **2.0Gi** |

## API Endpoints

### Authentication (`/api/v1/auth`)
- `POST /register` - Register a new user
- `POST /login` - Login (returns access + refresh tokens)
- `POST /logout` - Logout current user
- `GET /session` - Get current session info

### Tasks (`/api/v1/tasks`)
- `GET /` - List tasks (supports filtering by priority, tags, due_date, search, pagination)
- `POST /` - Create a new task
- `GET /{id}` - Get a specific task
- `PUT /{id}` - Update a task
- `DELETE /{id}` - Delete a task (soft delete)
- `PATCH /{id}/complete` - Toggle completion status
- `PATCH /{id}/recurring` - Set recurring pattern (RFC 5545)
- `PATCH /{id}/due_date` - Update due date

### Chat (`/api/v1/chat`)
- `POST /` - Send message to AI assistant (creates tasks via natural language)
- `GET /conversations` - List all conversations
- `GET /conversations/{id}` - Get conversation with messages

### Tags (`/api/v1/tags`)
- `GET /` - List user's tags
- `POST /` - Create a tag
- `PUT /{id}` - Update a tag
- `DELETE /{id}` - Delete a tag

### Health
- `GET /health` - Health check

## Security

- JWT tokens in httpOnly cookies (XSS protection)
- CSRF token validation on state-changing requests
- User data isolation via `user_id` filtering on all queries
- Input validation with Pydantic
- Secure password hashing (bcrypt)
- Non-root containers with read-only filesystem (K8s security context)

## Project Structure

```
flow/
├── backend/              # FastAPI backend
│   └── backend/src/
│       ├── main.py              # App entry + routes
│       ├── models.py            # SQLModel entities
│       ├── auth.py              # JWT + Better Auth
│       ├── chat.py              # AI chat with Groq
│       └── dapr_event_publisher.py  # Dapr pub/sub client
├── frontend/             # Next.js frontend
│   └── src/
│       ├── app/                 # App router pages
│       ├── components/          # React components
│       └── lib/                 # Auth + API utilities
├── k8s/                  # Kubernetes manifests & Helm charts
├── specs/                # SDD specifications & plans
├── history/adr/          # Architecture Decision Records
└── pptx-workspace/       # Hackathon presentation source
```

## Architecture Decision Records

Key decisions documented in `history/adr/`:

| ADR | Decision |
|-----|----------|
| ADR-001 | JWT Token Storage (httpOnly cookies) |
| ADR-002 | Application-Level User Isolation |
| ADR-003 | Soft Delete Strategy |
| ADR-004 | Task Tags Storage Approach |
| ADR-005 | API Extension Strategy |
| ADR-0001 | Kafka Infrastructure Stack |
| ADR-0004 | Dapr Runtime and SDK Integration |
| ADR-0005 | Event Transport Migration to Dapr Pub/Sub |
| ADR-0007 | Ingress Traffic Routing and OCI Load Balancer |
| ADR-0008 | Kafka on Free-Tier OKE (KRaft mode) |
| ADR-0009 | Dapr Sidecar Injection and Graceful Degradation |
| ADR-0011 | Resource Budget and Helm Template Strategy |

## License

MIT
