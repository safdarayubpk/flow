# Quickstart Guide: Advanced Todo Features

## Overview
This guide provides a quick introduction to implementing the advanced todo features including priorities, tags, search/filter, sort, recurring tasks, and due date reminders.

## Prerequisites
- Python 3.13+ with uv package manager
- Node.js 18+ with npm/yarn
- PostgreSQL database (Neon recommended)
- Next.js 16+ environment

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Update DATABASE_URL, JWT_SECRET, and other required variables
   ```

4. Run database migrations:
   ```bash
   # Using alembic for migrations
   alembic upgrade head
   ```

5. Start the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   # or
   yarn install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Update NEXT_PUBLIC_API_URL to point to your backend
   ```

4. Start the development server:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

## Key Features Implementation

### 1. Priority Levels
- Implement priority field in Task model (high/medium/low)
- Create PriorityBadge component for UI display
- Add priority filtering and sorting capabilities

### 2. Tag Management
- Implement Tag entity with many-to-many relationship to Task
- Create TagChips component for tag display
- Implement tag creation, assignment, and search functionality

### 3. Advanced Search & Filter
- Add query parameters to GET /api/tasks endpoint
- Implement filtering by priority, tags, due date range
- Add sorting by priority, due date, title

### 4. Recurring Tasks
- Add recurrence_rule field to Task model (RRULE format)
- Implement recurring task creation and management
- Create recurrence pattern selector UI

### 5. Due Date Reminders
- Add due_date and reminder_enabled fields to Task model
- Implement browser notification handling
- Create date/time picker component

## API Endpoints

### Extended Task Endpoints
- `GET /api/v1/tasks` - List tasks with new query parameters:
  - `priority`: Filter by priority (high/medium/low)
  - `tags`: Filter by tags (comma-separated)
  - `due_date_before`: Filter tasks with due dates before date
  - `sort`: Sort by field (priority/due_date/title/created_at)
  - `recurring`: Filter recurring tasks only (true/false)

- `PATCH /api/v1/tasks/{id}/recurring` - Update recurring settings
- `PATCH /api/v1/tasks/{id}/due_date` - Update due date

## Database Schema Changes

### Task Table Extensions
- `priority`: VARCHAR(10), INDEX
- `tags`: JSONB column
- `due_date`: TIMESTAMP, INDEX
- `recurrence_rule`: TEXT
- `reminder_enabled`: BOOLEAN, DEFAULT FALSE

### New Tables
- `tag`: Stores tag definitions
- `task_tags`: Association table for task-tag relationships

## UI Components

### New Components
- `PriorityBadge`: Displays priority level with color coding
- `TagChips`: Displays tags as colored chips with removal option
- `DatePicker`: Date/time picker for due dates
- `RecurringToggle`: Toggle for recurring task settings
- `SortDropdown`: Dropdown for sorting options

### Updated Components
- `TaskForm`: Extended with priority, tags, due date, recurrence inputs
- `TaskCard`: Enhanced with priority badges and tag chips display

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret for JWT token generation
- `BETTER_AUTH_SECRET`: Secret for Better Auth
- `OPENAI_API_KEY`: API key for AI features (optional)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Authentication URL

## Running Tests

### Backend Tests
```bash
pytest tests/
```

### Frontend Tests
```bash
npm run test
# or
yarn test
```

## Deployment

### Local Development
- Use the setup instructions above for local development

### Kubernetes Deployment
- Use the provided Helm charts in the k8s/ directory
- Configure secrets and values before deployment

## Troubleshooting

### Common Issues
1. **Database migration errors**: Ensure PostgreSQL is accessible and credentials are correct
2. **Tag search not working**: Check that the tag relationship is properly implemented
3. **Notifications not appearing**: Verify browser notification permissions are granted
4. **Recurring tasks not generating**: Check RRULE format validity

### Debugging Tips
- Enable logging to see detailed request/response information
- Verify user_id filtering is working properly for isolation
- Check that all new indexes are created for performance