# Feature Specification: Local Kubernetes Deployment with Minikube

**Feature Branch**: `004-k8s-minikube-deployment`
**Created**: 2026-01-27
**Status**: Draft
**Input**: User description: "Phase IV: Local Kubernetes Deployment with Minikube

Target audience: Beginner learning Kubernetes for the first time.

Focus: Containerize the existing Todo app (frontend Next.js + backend FastAPI) and deploy both to a local Minikube cluster so the full app (login + tasks + AI Chatbot) works inside Kubernetes — while keeping the existing Vercel + Hugging Face deployments completely unaffected.

Important environment precondition (already satisfied by user):
- Docker Desktop is installed and running
- Minikube v1.37.0 is installed and can start with Docker driver
- kubectl v1.35.x is installed and connected to Minikube
- Helm v4.1.0 is installed and working
- kubectl-ai is installed and functional
- All tools have been verified: cluster starts, helm list works, etc.
Do NOT generate any installation steps for these tools — assume they are ready.
Focus only on writing Dockerfiles, Helm charts/manifests, and deployment steps.

Success criteria:
- Separate Dockerfiles for frontend and backend (do NOT overwrite existing backend/Dockerfile used for Hugging Face Spaces)
- Images built locally and loaded into Minikube (using minikube image load)
- Minikube cluster starts successfully
- Helm chart (preferred) or basic manifests deploy backend (Deployment + Service)
- Helm chart/manifests deploy frontend (Deployment + Service)
- Frontend talks to backend using Kubernetes service name (not localhost or external URLs)
- Access the app locally via port-forward or minikube service
- kubectl-ai used at least once to help create, explain, or debug YAML
- Full app works inside Minikube: login → AI Chat → add/show/complete tasks via natural language
- No cloud resources used (all local)
- Existing Vercel frontend and Hugging Face backend deployments remain 100% unchanged and functional

Constraints:
- Use Docker + Minikube + Helm (preferred) or basic kubectl manifests
- Keep it simple — no Ingress, no external database (reuse existing Neon or add a simple in-cluster Postgres pod only if absolutely needed)
- No Kafka/Dapr yet (save for Phase V)
- All code/YAML generated via SDD workflow and active skills (especially kubernetes-yaml-best-practices, helm-chart-todo-app, minikube-local-deployment-pattern, k8s-security-basics)
- Explain everything in beginner-friendly language with comments and simple steps
- Timeline: Complete locally testable deployment

Not building in this phase:
- Real cloud deployment (DigitalOcean DOKS)
- Advanced features (Kafka, Dapr, scaling, autoscaling)
- Public internet exposure
- Any changes to existing Vercel or Hugging Face deployments

After generating the specification, automatically suggest running /sp.clarify to make sure nothing is confusing for a beginner."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Full Todo App to Minikube (Priority: P1)

As a beginner learning Kubernetes, I want to containerize and deploy the existing Todo app (frontend Next.js + backend FastAPI) to a local Minikube cluster so that I can learn Kubernetes concepts while using the familiar app I built. The app should work completely within Kubernetes with login, task management, and AI chatbot functionality.

**Why this priority**: This is the core learning objective - to deploy the full application stack to Kubernetes for hands-on learning experience.

**Independent Test**: Can be fully tested by deploying both frontend and backend to Minikube and verifying all functionality works end-to-end without connecting to external services.

**Acceptance Scenarios**:

1. **Given** Minikube is running and Docker images are built, **When** I deploy the Helm charts for both frontend and backend, **Then** both services are running in the cluster and accessible.

2. **Given** Both services are deployed to Minikube, **When** I access the frontend via port-forward or minikube service, **Then** I can login, use the AI chatbot, and manage tasks without connecting to external services.

---

### User Story 2 - Containerize Frontend and Backend Applications (Priority: P1)

As a developer, I want to create separate Dockerfiles for the frontend Next.js and backend FastAPI applications so that I can build container images that work independently within the Kubernetes cluster.

**Why this priority**: Containerization is fundamental to Kubernetes deployment and allows for consistent environments across development and deployment.

**Independent Test**: Can be fully tested by building Docker images locally and verifying they start and serve content properly.

**Acceptance Scenarios**:

1. **Given** source code for frontend and backend exist, **When** I build Docker images using the created Dockerfiles, **Then** images are created successfully without errors.

2. **Given** Docker images are built, **When** I run them locally with docker run, **Then** they start and serve content as expected.

---

### User Story 3 - Configure Service Communication in Kubernetes (Priority: P2)

As a developer, I want to configure the frontend to communicate with the backend using Kubernetes service names instead of external URLs so that both services can communicate within the cluster.

**Why this priority**: Internal service communication is essential for proper Kubernetes networking and allows the app to function as a cohesive unit within the cluster.

**Independent Test**: Can be tested by deploying both services and verifying they can communicate using Kubernetes service names.

**Acceptance Scenarios**:

1. **Given** both frontend and backend services are deployed in Minikube, **When** the frontend makes API calls to the backend using the Kubernetes service name, **Then** the requests succeed and data flows correctly between services.

---

### User Story 4 - Access Deployed Application Locally (Priority: P2)

As a learner, I want to access the deployed application locally via port-forward or minikube service so that I can interact with the application running in Kubernetes.

**Why this priority**: Accessibility is essential for testing and learning - users need to interact with the deployed application to verify it works.

**Independent Test**: Can be tested by accessing the deployed application and verifying the UI loads and responds to user interactions.

**Acceptance Scenarios**:

1. **Given** application is deployed to Minikube, **When** I use minikube service or kubectl port-forward to access it, **Then** the application UI loads and functions properly.

---

### User Story 5 - Use kubectl-ai for YAML Generation and Debugging (Priority: P3)

As a developer learning Kubernetes, I want to use kubectl-ai to help create, explain, or debug YAML manifests so that I can better understand Kubernetes concepts and troubleshoot issues.

**Why this priority**: This enhances the learning experience by providing AI assistance for understanding and debugging Kubernetes configurations.

**Independent Test**: Can be tested by using kubectl-ai to generate or explain Kubernetes YAML and verify it's accurate.

**Acceptance Scenarios**:

1. **Given** I need to create or understand Kubernetes YAML, **When** I use kubectl-ai, **Then** it provides helpful explanations or generates valid YAML.

---

### Edge Cases

- What happens when Minikube cluster is low on resources and pods fail to start?
- How does the system handle network connectivity issues between frontend and backend services?
- What if the database connection from the backend to Neon fails in the Kubernetes environment?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST containerize the existing frontend Next.js application with a separate Dockerfile
- **FR-002**: System MUST containerize the existing backend FastAPI application with a separate Dockerfile (without overwriting existing Hugging Face Spaces Dockerfile)
- **FR-003**: System MUST build Docker images locally and load them into Minikube using minikube image load
- **FR-004**: System MUST deploy backend FastAPI service to Minikube with Deployment and Service manifests
- **FR-005**: System MUST deploy frontend Next.js service to Minikube with Deployment and Service manifests
- **FR-006**: System MUST configure frontend to communicate with backend using Kubernetes service name (not external URLs)
- **FR-007**: System MUST provide access to the application via port-forward or minikube service
- **FR-008**: System MUST use Helm charts (preferred) or basic manifests for deployment
- **FR-009**: System MUST ensure full app functionality works: login → AI Chat → add/show/complete tasks via natural language
- **FR-010**: System MUST preserve existing Vercel frontend and Hugging Face backend deployments (no changes)
- **FR-011**: System MUST utilize kubectl-ai at least once for YAML generation or debugging
- **FR-012**: System MUST follow beginner-friendly practices with comments and simple steps
- **FR-013**: System MUST reuse existing Neon PostgreSQL database connection (no new database required unless absolutely necessary)
- **FR-014**: System MUST apply basic security context to deployments including runAsNonRoot, readOnlyRootFilesystem, and resource limits
- **FR-015**: System MUST manage environment variables using Kubernetes ConfigMaps and Secrets
- **FR-016**: System MUST use Kubernetes native service discovery via DNS names for service communication

### Key Entities *(include if feature involves data)*

- **Todo Application**: The existing full-stack application consisting of frontend Next.js UI and backend FastAPI services
- **Kubernetes Resources**: Deployment, Service, and ConfigMap resources for managing the application in Minikube
- **Docker Images**: Containerized versions of frontend and backend applications
- **Network Configuration**: Internal service communication setup allowing frontend to talk to backend within the cluster
- **Database Connection**: Neon PostgreSQL database connection reused from existing application configuration
- **Environment Configuration**: Kubernetes ConfigMaps and Secrets for managing environment variables

## Clarifications

### Session 2026-01-27

- Q: Which database approach should be used for the Minikube deployment? → A: Reuse the existing Neon PostgreSQL database connection
- Q: What level of security context should be applied to the deployments? → A: Apply basic security context with runAsNonRoot, readOnlyRootFilesystem, and resource limits
- Q: How should environment variables be managed in the Kubernetes deployment? → A: Use Kubernetes ConfigMaps and Secrets to pass environment variables to the containers
- Q: How should the frontend communicate with the backend service in Kubernetes? → A: Use Kubernetes native service discovery via DNS names (backend-service.default.svc.cluster.local)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can successfully deploy both frontend and backend applications to Minikube cluster and access the full application functionality
- **SC-002**: Application demonstrates all core features working: login, AI chatbot, task management (add/show/complete tasks via natural language) within the Kubernetes environment
- **SC-003**: User can access the application via minikube service or kubectl port-forward within 5 minutes of deployment
- **SC-004**: All existing Vercel and Hugging Face deployments remain unchanged and fully functional after local Kubernetes deployment
- **SC-005**: At least one kubectl-ai command is successfully used to generate, explain, or debug Kubernetes YAML manifests
- **SC-006**: Beginner user can understand and reproduce the deployment process following the documented steps
- **SC-007**: No external cloud resources are consumed during local Minikube deployment (all resources contained within local environment)
