# Data Model: Console Todo App

## Task Entity

### Attributes
- **ID**: `int` - Unique sequential integer identifier (auto-assigned)
- **Title**: `str` - Short text describing the task (required, non-empty)
- **Description**: `str` - Optional longer text with additional details
- **Completed**: `bool` - Boolean status indicating if task is done (defaults to false)
- **Created_At**: `datetime` - Timestamp of creation (auto-assigned)

### Relationships
- None (self-contained entity)

### Validation Rules
- Title must be non-empty string
- ID must be unique within the application session
- ID must be positive integer
- Created_At must be set at creation time

### State Transitions
- Default state: `completed = false`
- Toggle operation: `completed = not completed`

## In-Memory Storage

### Data Structure
- `tasks: Dict[int, Task]` - Dictionary mapping task IDs to Task objects
- `next_id: int` - Counter for assigning next available ID (starts at 1)

### Operations
- **Create**: Add new Task to dictionary with next available ID
- **Read**: Retrieve Task by ID from dictionary
- **Update**: Modify existing Task in dictionary
- **Delete**: Remove Task from dictionary by ID
- **List**: Return all Tasks in dictionary as list

## Error Handling
- **Non-existent ID**: Raise `TaskNotFoundError` or return None
- **Empty title**: Raise `ValidationError` during creation/update
- **Duplicate ID**: Should not occur with auto-increment mechanism