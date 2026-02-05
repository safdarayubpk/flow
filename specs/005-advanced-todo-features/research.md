# Research Document: Advanced Todo Features

## Overview

This document consolidates research findings for implementing advanced todo features including priorities, tags, search/filter, sort, recurring tasks, and due date reminders. The research addresses all technical unknowns and establishes the foundation for the implementation.

## Decision: Task Model Extension Approach
**Rationale**: Extend the existing Task SQLModel with new fields while preserving all existing functionality and maintaining backward compatibility. This approach minimizes disruption to existing features while enabling new capabilities.
**Alternatives considered**: Separate extension tables, inheritance patterns, JSON fields for all new attributes. Chosen approach balances simplicity with performance.

## Decision: Database Migration Strategy
**Rationale**: Use Alembic with SQLModel migrations to safely add new columns to the existing Task table. This ensures zero data loss and provides rollback capabilities.
**Alternatives considered**: Manual schema updates, direct SQL execution. Alembic provides safer, version-controlled migrations.

## Decision: UI Component Library
**Rationale**: Use shadcn/ui components with Tailwind CSS for consistency and maintainability. Leverages proven UI patterns while ensuring accessibility.
**Alternatives considered**: Custom components from scratch, Material UI, Chakra UI. shadcn/ui integrates well with the existing tech stack.

## Decision: Tag Storage Implementation
**Rationale**: Implement tags as a separate entity with many-to-many relationship to tasks via an association table. This allows for efficient querying and tag management while maintaining data integrity.
**Alternatives considered**: JSON field in Task table, denormalized approach. Separate entity provides better query performance and normalization.

## Decision: Recurring Task Implementation
**Rationale**: Implement recurring tasks using RRULE strings stored in the task entity with separate instances generated as needed. This follows standard calendar patterns and provides flexibility.
**Alternatives considered**: Template-based approach, cron expressions. RRULE provides standard, well-supported recurrence patterns.

## Decision: Notification Strategy
**Rationale**: Implement both browser notifications and in-app toast notifications with fallback from browser to in-app when permissions are denied. This ensures functionality regardless of user preferences.
**Alternatives considered**: Email notifications, push notifications. Browser/in-app notifications provide immediate feedback with minimal setup.

## Decision: Search and Filter Implementation
**Rationale**: Implement server-side filtering with query parameters for scalability. This allows for efficient searching across large datasets while maintaining security through user isolation.
**Alternatives considered**: Client-side filtering, full-text search engines. Server-side filtering provides better security and performance for the expected scale.

## Decision: Timezone Handling
**Rationale**: Store all times in UTC in the database and convert to user's local timezone for display. This handles timezone differences for recurring tasks across different timezones.
**Alternatives considered**: Store in user's local timezone. UTC storage provides consistency and avoids issues with daylight saving time changes.

## Decision: API Endpoint Design
**Rationale**: Extend existing API endpoints with new query parameters for filtering and sorting rather than creating entirely new endpoints. This maintains consistency with existing patterns.
**Alternatives considered**: Separate advanced endpoints. Extension maintains consistency and reduces API surface area.