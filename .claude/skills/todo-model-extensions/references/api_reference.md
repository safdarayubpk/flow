# SQLModel Task Extension Reference

This document provides detailed reference information for extending the Task SQLModel with additional fields while maintaining backward compatibility.

## SQLModel Field Extensions

### Priority Field
```python
from typing_extensions import Literal
from typing import Optional

priority: Optional[Literal["high", "medium", "low"]] = Field(default=None, index=True)
```

- Type: Optional literal with three possible values
- Index: Enabled for fast queries
- Default: None

### Tags Field
```python
from typing import List
from sqlalchemy import Column, JSON

tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
```

- Type: List of strings stored as JSON in database
- Default: Empty list
- Storage: JSON column type in database

### Due Date Field
```python
from datetime import datetime
from typing import Optional

due_date: Optional[datetime] = Field(default=None, index=True)
```

- Type: Optional datetime
- Index: Enabled for fast date range queries
- Default: None

### Recurrence Rule Field
```python
from typing import Optional

recurrence_rule: Optional[str] = None  # RRULE string
```

- Type: Optional string
- Format: RFC 5545 RRULE format
- Default: None

### Reminder Enabled Field
```python
reminder_enabled: bool = False
```

- Type: Boolean
- Default: False

## Database Migration Patterns

### Adding Fields with Alembic
```python
# In your alembic migration file
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Add priority field
    op.add_column('task', sa.Column('priority', sa.String(10), nullable=True))
    op.create_index('ix_task_priority', 'task', ['priority'])

    # Add tags field as JSON
    op.add_column('task', sa.Column('tags', postgresql.JSONB, nullable=True, server_default='[]'))

    # Add due_date field
    op.add_column('task', sa.Column('due_date', sa.DateTime, nullable=True))
    op.create_index('ix_task_due_date', 'task', ['due_date'])

    # Add recurrence_rule field
    op.add_column('task', sa.Column('recurrence_rule', sa.Text, nullable=True))

    # Add reminder_enabled field
    op.add_column('task', sa.Column('reminder_enabled', sa.Boolean, nullable=True, server_default='false'))

def downgrade():
    op.drop_column('task', 'reminder_enabled')
    op.drop_column('task', 'recurrence_rule')
    op.drop_index('ix_task_due_date')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'tags')
    op.drop_index('ix_task_priority')
    op.drop_column('task', 'priority')
```

## Service Layer Updates

When extending the Task model, update related services to handle new fields:

```python
# In task_service.py
def create_task(session: Session, task_create: TaskCreate, user_id: str):
    # Include new fields in creation
    task_data = task_create.dict()
    task_data["user_id"] = user_id

    db_task = Task(**task_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def update_task(session: Session, task_id: int, task_update: TaskUpdate, user_id: str):
    db_task = session.get(Task, task_id)
    if not db_task or db_task.user_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update with new fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
```

## Query Optimization

With new indexed fields, optimize common queries:

```python
from sqlmodel import select
from datetime import datetime

# Get high priority tasks for a user
high_priority_tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id, Task.priority == "high")
    .order_by(Task.created_at.desc())
).all()

# Get overdue tasks
overdue_tasks = session.exec(
    select(Task)
    .where(
        Task.user_id == user_id,
        Task.due_date < datetime.now(),
        Task.completed == False
    )
    .order_by(Task.due_date)
).all()

# Get tasks with specific tags
tagged_tasks = session.exec(
    select(Task)
    .where(
        Task.user_id == user_id,
        func.jsonb_exists(Task.tags, "work")  # Example for JSONB
    )
).all()
```
