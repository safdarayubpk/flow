# Data Model: Advanced Todo Features

## Entity: Task (Extended)

### Fields
- `id`: int (Primary Key, Auto-generated)
- `user_id`: int (Foreign Key, Indexed, Required for user isolation)
- `title`: str (Required, Task title)
- `description`: Optional[str] (Optional, Task description)
- `completed`: bool (Default: False, Completion status)
- `created_at`: datetime (Auto-generated, Creation timestamp)
- `updated_at`: datetime (Auto-generated, Last update timestamp)
- `priority`: Optional[Literal["high", "medium", "low"]] (Indexed, Default: None, Priority level)
- `tags`: List[str] (Stored as JSON, Default: [], Associated tags)
- `due_date`: Optional[datetime] (Indexed, Default: None, Due date and time)
- `recurrence_rule`: Optional[str] (Default: None, RRULE string for recurrence pattern)
- `reminder_enabled`: bool (Default: False, Whether to enable reminders)

### Relationships
- `user`: User (Many-to-One, Task belongs to User)
- `tags`: List[Tag] (Many-to-Many via task_tags association table)

### Validation Rules
- `title`: 1-200 characters
- `priority`: Enum values only ("high", "medium", "low") or null
- `tags`: Each tag 1-50 alphanumeric characters with spaces, hyphens, underscores only
- `due_date`: Can be in the past (for historical tracking) but UI should warn
- `recurrence_rule`: Valid RRULE format when provided

### State Transitions
- `created` → `updated` → `completed` (with ability to toggle back to incomplete)
- `non-recurring` → `recurring` (when recurrence_rule is set)
- `reminder_disabled` → `reminder_enabled` (when reminder_enabled is set to True)

## Entity: Tag

### Fields
- `id`: int (Primary Key, Auto-generated)
- `name`: str (Required, Unique per user, 1-50 characters, alphanumeric + spaces/hyphens/underscores)
- `user_id`: int (Foreign Key, Indexed, Links tag to specific user)
- `created_at`: datetime (Auto-generated, Creation timestamp)

### Relationships
- `tasks`: List[Task] (Many-to-Many via task_tags association table)
- `user`: User (Many-to-One, Tag belongs to User)

### Validation Rules
- `name`: Unique per user, 1-50 characters, alphanumeric + spaces/hyphens/underscores only
- `name`: Case-insensitive comparison but stored as entered

## Association Table: task_tags

### Fields
- `task_id`: int (Foreign Key to Task, Indexed)
- `tag_id`: int (Foreign Key to Tag, Indexed)

### Constraints
- Composite primary key (task_id, tag_id)
- Prevents duplicate tag assignments to the same task

## Entity: User (Existing - Unchanged)

### Fields
- `id`: int (Primary Key, Auto-generated)
- `email`: str (Required, Unique)
- `created_at`: datetime (Auto-generated)
- `updated_at`: datetime (Auto-generated)

### Relationships
- `tasks`: List[Task] (One-to-Many, User has many Tasks)
- `tags`: List[Tag] (One-to-Many, User has many Tags)

## Indexes for Performance

### Task Table
- `idx_task_user_id`: Index on user_id (for user isolation queries)
- `idx_task_priority`: Index on priority (for priority-based filtering)
- `idx_task_due_date`: Index on due_date (for due date queries)
- `idx_task_completed`: Index on completed (for status filtering)

### Tag Table
- `idx_tag_user_id`: Index on user_id (for user-specific tag queries)
- `idx_tag_name`: Index on name (for tag name searches)

## Migration Plan

### Add Columns to Existing Task Table
1. Add `priority` column (VARCHAR, nullable, with index)
2. Add `tags` column (JSONB, default empty array)
3. Add `due_date` column (TIMESTAMP, nullable, with index)
4. Add `recurrence_rule` column (TEXT, nullable)
5. Add `reminder_enabled` column (BOOLEAN, default false)

### Create Tag Table
1. Create `tag` table with fields as defined above
2. Create `task_tags` association table with foreign keys
3. Add indexes as specified

### Data Migration
1. Convert existing tag strings in JSON format if they exist
2. Ensure all existing tasks have proper user_id associations
3. Update any existing data to conform to new validation rules