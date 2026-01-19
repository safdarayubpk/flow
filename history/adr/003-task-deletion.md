# ADR-003: Soft Delete Strategy for Task Management

## Status
Accepted

## Context
The application needs to handle task deletion in a persistent, user-owned system where data recovery and auditability are important. The deletion strategy affects data integrity, user experience, performance, and system complexity. Users may accidentally delete important tasks and need to recover them, while the system should maintain audit trails of user actions.

## Decision
Implement soft delete by adding a deleted_at timestamp field to the Task model and filtering out soft-deleted records in queries. Deleted tasks will be permanently removed after a retention period (e.g., 30 days) through scheduled cleanup jobs.

## Alternatives Considered
- **Hard Delete**: Pro: Simpler implementation, better performance, cleaner database; Con: No recovery option, loss of audit trail, irreversible mistakes
- **Soft Delete with retention**: Pro: Recovery capability, audit trail preserved, user protection from accidental deletion; Con: Increased complexity, performance impact from additional filters, growing database size
- **Archive Strategy**: Pro: Clear separation of active/inactive items, potential for user access to archived items; Con: Additional complexity, unclear UX for users

## Rationale
The soft delete approach was selected because it provides a safety net for users who accidentally delete tasks while maintaining the appearance of immediate deletion. The retention period allows for recovery while eventually cleaning up the database. This approach balances user experience (ability to recover mistakes) with system performance (eventual cleanup of deleted data). It also preserves audit trails for security and compliance purposes.

## Consequences
- **Positive**: User protection from accidental deletion, audit trail preservation, recovery capability
- **Negative**: Increased query complexity, performance impact, larger database size during retention period
- **Constraints**: Need to implement scheduled cleanup jobs, modify all queries to filter out deleted records, manage retention period policy