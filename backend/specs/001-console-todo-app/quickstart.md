# Quickstart: Console Todo App

## Prerequisites
- Python 3.13+
- UV package manager (optional but recommended)

## Setup
1. Clone the repository
2. Navigate to the project directory
3. Install dependencies (if any): `uv sync` or `pip install -r requirements.txt`

## Running the Application
```bash
cd src
python main.py
```

## Usage
Upon running the application, you will see a menu with the following options:
1. **Add Task** - Create a new task with title and optional description
2. **View Tasks** - Display all existing tasks with their status
3. **Update Task** - Modify the title or description of an existing task
4. **Delete Task** - Remove a task from the list
5. **Mark Complete/Incomplete** - Toggle the completion status of a task
6. **Quit** - Exit the application

## Example Workflow
1. Select "Add Task" to create a new task
2. Enter the task title and optional description
3. Select "View Tasks" to see your task list
4. Use "Mark Complete/Incomplete" to update task status
5. Use "Update Task" to modify task details
6. Use "Delete Task" to remove completed tasks
7. Select "Quit" when finished

## Features
- Interactive menu-driven interface
- Task management with title, description, and completion status
- In-memory storage (data is lost when application exits)
- Error handling for invalid inputs
- Sequential task IDs for easy reference