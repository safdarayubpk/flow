# ADR-004: Task Tags Storage Approach

## Status: Accepted
## Date: 2026-02-03

## Context
The system needs to support tagging tasks with multiple categories/labels. We must decide between storing tags as a JSON array directly in the Task table versus creating a separate Tag entity with a many-to-many relationship through an association table. This decision impacts query performance, data normalization, scalability, and future extensibility of tag functionality.

## Decision
We will implement tags as a separate entity with a many-to-many relationship to the Task entity via an association table named `task_tags`. This approach provides better normalization, more efficient querying capabilities, and supports future tag-centric features.

## Alternatives Considered

**Alternative 1: JSON Array in Task Table**
- Pros: Simpler initial implementation, fewer joins, single query for task with tags
- Cons: Limited querying capabilities, potential performance issues with large tag lists, less normalized data structure, difficult to implement tag-centric features

**Alternative 2: Separate Tag Entity with Many-to-Many Relationship (Chosen)**
- Pros: Better normalization, efficient querying on tags, supports tag statistics and analytics, enables tag-based filtering and search, maintains referential integrity
- Cons: Requires joins, slightly more complex initial implementation, additional database tables

## Rationale
The many-to-many approach provides superior query performance for tag-based filtering, which is a core requirement. It enables efficient implementation of search/filter functionality by tags as specified in the requirements. This approach also supports future scalability needs such as tag analytics, tag permissions, or tag hierarchies.

## Consequences
**Positive:**
- Efficient tag-based queries and filtering
- Better data normalization and integrity
- Support for advanced tag features in future iterations
- Proper separation of concerns between tasks and tags

**Negative:**
- Slightly more complex initial implementation
- Additional database queries requiring joins
- More tables to maintain

**Constraints:**
- Requires proper indexing strategy for tag-based queries
- Need to handle association table maintenance in application logic