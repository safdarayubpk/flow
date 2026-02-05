# ADR-006: Time Storage and Display Strategy

## Status: Accepted
## Date: 2026-02-03

## Context
The system needs to handle task due dates and recurring tasks across different time zones. We must decide how to store and display time information to ensure consistency, proper handling of recurring tasks across time zone changes, and accurate scheduling. This affects data integrity, user experience, and system reliability.

## Decision
We will store all times in UTC in the database and convert to the user's local timezone for display. This ensures consistency across the system while properly handling timezone differences for recurring tasks.

## Alternatives Considered

**Alternative 1: UTC Storage with Local Timezone Conversion (Chosen)**
- Pros: Consistent storage format, handles daylight saving time changes properly, supports users across multiple timezones, reliable for recurring tasks
- Cons: Requires client-side timezone detection, additional complexity for time display

**Alternative 2: Store in User's Local Timezone**
- Pros: Simpler display logic, matches user's local time directly
- Cons: Problems with daylight saving time transitions, issues when users travel, complications with recurring tasks

## Rationale
UTC storage provides the most reliable approach for handling time across different timezones and is essential for proper recurring task functionality. This approach handles daylight saving time transitions automatically and ensures consistency regardless of user location or timezone changes. For recurring tasks, UTC storage prevents issues when daylight saving time changes occur.

## Consequences
**Positive:**
- Reliable handling of recurring tasks across timezones
- Consistent time storage regardless of user location
- Proper handling of daylight saving time transitions
- Supports global user base

**Negative:**
- Requires timezone detection on client-side
- More complex time display logic
- Potential confusion if timezone detection fails

**Constraints:**
- Client-side timezone detection required
- Proper handling of timezone-aware datetime objects
- Consistent timezone conversion across all time operations