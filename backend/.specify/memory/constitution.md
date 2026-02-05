<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 1.0.0
Bump rationale: Constitution update to enhance clarity and structure for Hackathon II project

Modified principles: All principles revised for greater specificity and clarity

Added sections:
  - Tech Stack and Standards with detailed technology matrix
  - Code Quality Standards
  - Testing Standards
  - Documentation Standards
  - Development Workflow and Constraints with monorepo structure
  - Deployment Progression
  - Constraints section
  - Bonus Feature Alignment
  - Detailed governance procedures

Removed sections: None (revisions only)

Templates requiring updates:
  - .specify/templates/plan-template.md - ⚠️ Pending review for alignment with new principles
  - .specify/templates/spec-template.md - ⚠️ Pending review for alignment with new principles
  - .specify/templates/tasks-template.md - ⚠️ Pending review for alignment with new workflow

Follow-up TODOs:
  - Review and update templates to align with new constitutional principles
  - Verify all workflow commands are properly referenced
==================
-->

# Hackathon II - Evolution of Todo App Constitution

## Core Principles

### I. Spec-Driven Development

All implementation MUST follow strict Spec-Driven Development (SDD) methodology:

- **No code generation** MUST occur until specifications, plans, and tasks are complete and validated
- Feature specifications (`spec.md`) MUST define user scenarios, functional requirements, and success criteria
- Implementation plans (`plan.md`) MUST establish technical context, architecture decisions, and project structure
- Task lists (`tasks.md`) MUST break work into testable, dependency-ordered units
- All artifacts MUST be reviewed and approved before proceeding to implementation

**Rationale**: SDD ensures alignment between stakeholder intent and delivered functionality. Judges evaluate both the process artifacts and final output, making documentation quality as important as code quality.

### II. AI-Only Implementation

All code MUST be generated exclusively by Claude Code:

- **No manual code writing** or direct human edits are permitted
- When generated code is incorrect, the response MUST be to refine specifications and plans, not to manually fix code
- Iterative refinement of artifacts MUST continue until Claude Code produces correct output
- Code review focuses on artifact quality that led to generation, not post-hoc human modifications

**Rationale**: This constraint demonstrates the power of well-crafted specifications and validates the SDD approach. It also ensures reproducibility—any developer with the same specifications should get equivalent output.

### III. Iterative Evolution

Development MUST proceed incrementally across the 5-phase progression:

- **Phase I**: Local console application
- **Phase II**: Web frontend + authenticated backend
- **Phase III**: AI chatbot integration
- **Phase IV**: Kubernetes deployment (Minikube)
- **Phase V**: Production cloud (DigitalOcean Kubernetes)

Each phase MUST:
- Build upon prior phase functionality without breaking it
- Maintain backward compatibility where architecturally feasible
- Include migration paths for schema and API changes
- Be independently demonstrable and testable

**Rationale**: Incremental delivery reduces risk, enables early feedback, and demonstrates progressive capability evolution—a key hackathon evaluation criterion.

### IV. Reusability and Modularity

All components MUST favor reusability and modular design:

- Code MUST follow SOLID and DRY principles
- Agent skills, MCP tools, and services MUST be designed for scalability and reuse
- Shared functionality MUST be extracted into reusable modules
- Component boundaries MUST be clearly defined with explicit interfaces
- Intelligence patterns (prompts, agent behaviors) MUST be captured for reuse

**Rationale**: Modular architecture enables parallel development, simplifies testing, and prepares the system for bonus features like multi-language support and voice integration.

### V. Security and Isolation

From Phase II onward, all implementations MUST enforce security and data isolation:

- User authentication MUST use JWT tokens via Better Auth
- All data queries MUST include per-user filtering
- Secrets and tokens MUST be stored in environment variables (`.env`)
- API endpoints MUST validate authentication and authorization
- Security events MUST be logged for audit purposes
- Cross-user data access MUST be explicitly prevented at the service layer

**Rationale**: Multi-tenant isolation is fundamental to any production application. Early enforcement prevents security debt and demonstrates production-readiness.

### VI. Cloud-Native Readiness

All architecture decisions MUST consider cloud-native deployment from the start:

- Services MUST be designed for loose coupling
- Event-driven patterns MUST use Dapr and Kafka/Redpanda where applicable
- All components MUST be containerizable with Docker
- Configuration MUST be externalized for Kubernetes deployment
- Horizontal scaling MUST be architecturally supported
- Health checks and graceful shutdown MUST be implemented

**Rationale**: Designing for cloud-native from Phase I avoids costly refactoring in Phases IV-V. The target deployment (DigitalOcean Kubernetes) requires these patterns.

## Tech Stack and Standards

### Approved Technology Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js (App Router) | Tailwind CSS for styling |
| Backend | FastAPI | Type-annotated Python |
| ORM | SQLModel | SQLAlchemy-based |
| Database | Neon PostgreSQL | Serverless PostgreSQL |
| Authentication | Better Auth | JWT-based |
| AI/Agents | OpenAI Agents SDK | Phase III+ |
| MCP | Official MCP SDK | Tool integrations |
| Containers | Docker | All services |
| Orchestration | Minikube/Helm (dev), DigitalOcean K8s (prod) | Phase IV-V |
| Events | Dapr, Kafka/Redpanda | Async messaging |
| Python Management | UV | Package management |

### Code Quality Standards

- All Python code MUST include type annotations
- All functions MUST include meaningful docstrings
- Code MUST follow PEP 8 (Python) and ESLint/Prettier (TypeScript)
- Comments MUST explain "why" not "what"
- Variable and function names MUST be descriptive and self-documenting

### Testing Standards

- Unit tests MUST cover core business logic
- Integration tests MUST validate API contracts
- Tests MUST validate against acceptance criteria in specifications
- Test coverage targets SHOULD aim for high coverage on critical paths

### Documentation Standards

- README MUST include setup, usage, and architecture overview
- Specifications MUST be maintained in `specs/` directory
- CLAUDE.md files MUST provide layer-specific guidance
- Decisions MUST be tracked via ADRs in `history/adr/`
- Prompt history MUST be recorded in `history/prompts/`

## Development Workflow and Constraints

### Monorepo Structure

```
/
├── specs/
│   ├── features/
│   ├── api/
│   ├── database/
│   └── ui/
├── backend/
├── frontend/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   └── templates/
├── history/
│   ├── prompts/
│   └── adr/
├── CLAUDE.md
└── README.md
```

### Workflow Sequence

1. **Specify** (`/sp.specify`): Create or update feature specification
2. **Clarify** (`/sp.clarify`): Resolve ambiguities via targeted questions
3. **Plan** (`/sp.plan`): Generate implementation plan with architecture decisions
4. **Tasks** (`/sp.tasks`): Create dependency-ordered, testable task list
5. **Analyze** (`/sp.analyze`): Validate cross-artifact consistency
6. **Implement** (`/sp.implement`): Execute tasks via Claude Code generation
7. **Commit** (`/sp.git.commit_pr`): Git workflow for commits and PRs

### Deployment Progression

| Phase | Deployment Target |
|-------|------------------|
| I | Local console execution |
| II-III | Vercel (frontend) + hosted backend |
| IV | Minikube local Kubernetes |
| V | DigitalOcean Kubernetes |

### Constraints

- **No unsupported libraries**: All dependencies MUST be compatible with UV and the approved stack
- **Artifact-only refinement**: Errors are fixed by improving specs, not manual code edits
- **Layered CLAUDE.md**: Each directory MAY have a CLAUDE.md with layer-specific rules

### Bonus Feature Alignment

The architecture MUST support optional bonus features:
- Reusable intelligence patterns (agent skills, prompts)
- Multi-language support (including Urdu)
- Voice interface integration
- Blueprint generation for reproducibility

## Governance

### Amendment Procedure

1. Propose amendment with rationale in a PHR or discussion
2. Document impact on existing artifacts
3. Update constitution with version increment
4. Propagate changes to affected templates
5. Create ADR for significant changes

### Versioning Policy

- **MAJOR**: Backward-incompatible principle changes or removals
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording, or non-semantic refinements

### Compliance Review

- All PRs MUST verify compliance with constitution principles
- Complexity beyond stated principles MUST be justified
- Violations MUST be documented and approved before merge
- Constitution supersedes conflicting guidance in other documents

**Version**: 1.0.0 | **Ratified**: 2026-01-17 | **Last Amended**: 2026-01-17
