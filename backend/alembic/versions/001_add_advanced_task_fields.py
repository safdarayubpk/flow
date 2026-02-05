"""Add advanced task fields

Revision ID: 001_add_advanced_task_fields
Revises:
Create Date: 2026-02-05 08:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes

# revision identifiers, used by Alembic.
revision: str = '001_add_advanced_task_fields'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to the task table
    op.add_column('task', sa.Column('priority', sa.String(length=20), nullable=True))
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('recurrence_rule', sa.String(length=200), nullable=True))


def downgrade() -> None:
    # Remove the columns from the task table
    op.drop_column('task', 'recurrence_rule')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'priority')