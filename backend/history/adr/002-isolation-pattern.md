# ADR-002: Application-Level User Isolation Pattern

## Status
Accepted

## Context
The multi-user todo application requires strict enforcement of user data isolation to prevent any cross-user data access. Every database operation must ensure that users can only access, modify, or delete their own tasks. The isolation enforcement pattern affects all data access layers and has significant implications for security, maintainability, and performance.

## Decision
Enforce user isolation at the application level by filtering all database queries with WHERE user_id = current_user.id. This approach implements the isolation logic in the service layer of the backend, ensuring that every data operation includes the user filter before execution.

## Alternatives Considered
- **Database Row-Level Security (RLS)**: Pro: Built-in security at database level, cannot be bypassed by application code; Con: Requires database-specific features, adds complexity, harder to test and debug
- **Separate Schemas per User**: Pro: Complete physical separation of data; Con: Excessive overhead, complex maintenance, poor scalability
- **Application-level filtering**: Pro: Centralized control, explicit and auditable, consistent across all operations; Con: Relies on developers remembering to include filter in every query

## Rationale
The application-level filtering approach was selected because it provides explicit, auditable control over data access while maintaining compatibility with standard SQL databases. Unlike database-specific solutions, this approach works with any SQL database and makes the security logic visible in the codebase. Although it relies on discipline to implement consistently, this can be addressed with helper functions and code reviews. The approach also allows for flexible business logic around data access beyond simple user isolation.

## Consequences
- **Positive**: Auditable security logic, database agnostic, flexible for complex access patterns
- **Negative**: Requires discipline to implement consistently, potential for human error
- **Constraints**: Need to implement helper functions and middleware to enforce consistent application of user filters