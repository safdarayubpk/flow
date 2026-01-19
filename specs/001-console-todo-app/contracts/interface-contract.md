# Console Interface Contract: Console Todo App

## Menu Options Contract
The application presents a menu with the following numbered options:

### Primary Operations
1. **Add Task** - Initiates task creation flow
2. **View Tasks** - Displays all tasks in the system
3. **Update Task** - Initiates task update flow
4. **Delete Task** - Initiates task deletion flow
5. **Mark Complete/Incomplete** - Initiates task completion toggle flow
6. **Quit** - Terminates the application

## Input/Output Contracts

### Add Task Flow
- **Input**: Title (required), Description (optional)
- **Validation**: Title must be non-empty
- **Output**: Success message with assigned ID, or error message
- **State Change**: New Task object added to in-memory store

### View Tasks Flow
- **Input**: None required
- **Output**: Formatted list of all tasks with ID, title, description, and completion status
- **Format**:
  ```
  ID | Status | Title | Description
  1  | [ ]    | Task 1 | Description here
  2  | [x]    | Task 2 | Another task
  ```

### Update Task Flow
- **Input**: Task ID (required), New title (optional), New description (optional)
- **Validation**: Task ID must exist, title must not be empty if provided
- **Output**: Success message or error message
- **State Change**: Existing Task object updated in in-memory store

### Delete Task Flow
- **Input**: Task ID (required)
- **Validation**: Task ID must exist
- **Output**: Success message or error message
- **State Change**: Task object removed from in-memory store

### Mark Complete/Incomplete Flow
- **Input**: Task ID (required)
- **Validation**: Task ID must exist
- **Output**: Success message or error message
- **State Change**: Task's completion status toggled in in-memory store

### Quit Flow
- **Input**: None
- **Output**: Goodbye message
- **State Change**: Application terminates gracefully

## Error Contract
All operations follow this error handling pattern:
- Invalid inputs result in descriptive error messages
- User is prompted to try again or return to main menu
- Application does not crash on invalid inputs
- Keyboard interrupts (Ctrl+C) are handled gracefully

## Data Contract
Task objects conform to this specification:
- ID: Unique sequential integer starting from 1
- Title: Non-empty string
- Description: Optional string
- Completed: Boolean (default: False)
- Created_At: Datetime stamp of creation