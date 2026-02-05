# API Contract: Advanced Task Management

## Overview
API contract for advanced task management features including priorities, tags, search/filter, sort, recurring tasks, and due date reminders.

## Base URL
`/api/v1/tasks`

## Authentication
All endpoints require authentication via JWT token in Authorization header:
`Authorization: Bearer <jwt_token>`

## Endpoints

### GET /api/v1/tasks
List tasks with advanced filtering and sorting capabilities.

**Query Parameters:**
- `priority` (optional): Filter by priority level (enum: "high", "medium", "low")
- `tags` (optional): Filter by tags (array of strings, comma-separated)
- `due_date_before` (optional): Filter tasks with due dates before this date (format: YYYY-MM-DD)
- `sort` (optional): Sort by field (enum: "priority", "due_date", "title", "created_at")
- `recurring` (optional): Filter recurring tasks only (boolean)
- `skip` (optional): Number of items to skip for pagination (default: 0, min: 0)
- `limit` (optional): Maximum number of items to return (default: 100, min: 1, max: 1000)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "title": "Complete project proposal",
    "description": "Finish and submit the project proposal",
    "completed": false,
    "priority": "high",
    "tags": ["work", "important"],
    "due_date": "2026-02-15T10:00:00",
    "recurrence_rule": "RRULE:FREQ=WEEKLY;INTERVAL=1",
    "reminder_enabled": true,
    "created_at": "2026-02-03T09:00:00",
    "updated_at": "2026-02-03T09:00:00"
  }
]
```

**Errors:**
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to access tasks
- 500: Internal Server Error - Unexpected server error

### POST /api/v1/tasks
Create a new task with advanced features.

**Request Body:**
```json
{
  "title": "New task",
  "description": "Task description (optional)",
  "priority": "medium",
  "tags": ["tag1", "tag2"],
  "due_date": "2026-02-15T10:00:00",
  "recurrence_rule": "RRULE:FREQ=WEEKLY;INTERVAL=1",
  "reminder_enabled": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 123,
  "title": "New task",
  "description": "Task description (optional)",
  "completed": false,
  "priority": "medium",
  "tags": ["tag1", "tag2"],
  "due_date": "2026-02-15T10:00:00",
  "recurrence_rule": "RRULE:FREQ=WEEKLY;INTERVAL=1",
  "reminder_enabled": false,
  "created_at": "2026-02-03T09:00:00",
  "updated_at": "2026-02-03T09:00:00"
}
```

**Errors:**
- 400: Bad Request - Invalid request body or validation errors
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to create tasks
- 500: Internal Server Error - Unexpected server error

### GET /api/v1/tasks/{task_id}
Get a specific task by ID.

**Path Parameters:**
- `task_id` (required): Task identifier

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Finish and submit the project proposal",
  "completed": false,
  "priority": "high",
  "tags": ["work", "important"],
  "due_date": "2026-02-15T10:00:00",
  "recurrence_rule": "RRULE:FREQ=WEEKLY;INTERVAL=1",
  "reminder_enabled": true,
  "created_at": "2026-02-03T09:00:00",
  "updated_at": "2026-02-03T09:00:00"
}
```

**Errors:**
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to access this task
- 404: Not Found - Task does not exist
- 500: Internal Server Error - Unexpected server error

### PUT /api/v1/tasks/{task_id}
Update a specific task by ID.

**Path Parameters:**
- `task_id` (required): Task identifier

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "priority": "low",
  "tags": ["updated", "tags"],
  "due_date": "2026-02-20T14:00:00",
  "recurrence_rule": "RRULE:FREQ=DAILY;INTERVAL=1",
  "reminder_enabled": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Updated task title",
  "description": "Updated description",
  "completed": true,
  "priority": "low",
  "tags": ["updated", "tags"],
  "due_date": "2026-02-20T14:00:00",
  "recurrence_rule": "RRULE:FREQ=DAILY;INTERVAL=1",
  "reminder_enabled": true,
  "created_at": "2026-02-03T09:00:00",
  "updated_at": "2026-02-03T10:00:00"
}
```

**Errors:**
- 400: Bad Request - Invalid request body or validation errors
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to update this task
- 404: Not Found - Task does not exist
- 500: Internal Server Error - Unexpected server error

### DELETE /api/v1/tasks/{task_id}
Delete a specific task by ID.

**Path Parameters:**
- `task_id` (required): Task identifier

**Response (204 No Content):**
No response body.

**Errors:**
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to delete this task
- 404: Not Found - Task does not exist
- 500: Internal Server Error - Unexpected server error

### PATCH /api/v1/tasks/{task_id}/recurring
Update recurring task settings.

**Path Parameters:**
- `task_id` (required): Task identifier

**Request Body:**
```json
{
  "recurrence_rule": "RRULE:FREQ=MONTHLY;INTERVAL=1",
  "recurrence_enabled": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Finish and submit the project proposal",
  "completed": false,
  "priority": "high",
  "tags": ["work", "important"],
  "due_date": "2026-02-15T10:00:00",
  "recurrence_rule": "RRULE:FREQ=MONTHLY;INTERVAL=1",
  "reminder_enabled": true,
  "created_at": "2026-02-03T09:00:00",
  "updated_at": "2026-02-03T10:00:00"
}
```

**Errors:**
- 400: Bad Request - Invalid request body or validation errors
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to update this task
- 404: Not Found - Task does not exist
- 500: Internal Server Error - Unexpected server error

### PATCH /api/v1/tasks/{task_id}/due_date
Update task due date.

**Path Parameters:**
- `task_id` (required): Task identifier

**Request Body:**
```json
{
  "due_date": "2026-02-25T16:00:00"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 123,
  "title": "Complete project proposal",
  "description": "Finish and submit the project proposal",
  "completed": false,
  "priority": "high",
  "tags": ["work", "important"],
  "due_date": "2026-02-25T16:00:00",
  "recurrence_rule": "RRULE:FREQ=WEEKLY;INTERVAL=1",
  "reminder_enabled": true,
  "created_at": "2026-02-03T09:00:00",
  "updated_at": "2026-02-03T10:00:00"
}
```

**Errors:**
- 400: Bad Request - Invalid request body or validation errors
- 401: Unauthorized - Invalid or missing JWT token
- 403: Forbidden - User not authorized to update this task
- 404: Not Found - Task does not exist
- 500: Internal Server Error - Unexpected server error

## Common Response Headers
- `Content-Type`: application/json
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets

## Error Response Format
All error responses follow this format:
```json
{
  "detail": "Descriptive error message"
}
```

## Validation Rules
- All timestamps must be in ISO 8601 format
- Priority values must be one of "high", "medium", "low" or null
- Tags must be arrays of strings with 1-50 alphanumeric characters plus spaces, hyphens, and underscores
- Due dates must be valid datetime values
- Recurrence rules must follow RFC 5545 RRULE format