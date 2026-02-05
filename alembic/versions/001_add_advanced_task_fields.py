"""Add advanced task fields

Revision ID: 001
Revises:
Create Date: 2026-02-03 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to the task table
    op.add_column('task', sa.Column('priority', sa.String(10), nullable=True))
    op.create_index('ix_task_priority', 'task', ['priority'])

    op.add_column('task', sa.Column('tags', postgresql.JSONB, nullable=True, server_default='[]'))
    op.create_index('ix_task_tags', 'task', ['tags'], postgresql_using='gin')

    op.add_column('task', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_task_due_date', 'task', ['due_date'])

    op.add_column('task', sa.Column('recurrence_rule', sa.Text, nullable=True))

    op.add_column('task', sa.Column('reminder_enabled', sa.Boolean, nullable=True, server_default='false'))


def downgrade():
    # Drop indexes
    op.drop_index('ix_task_due_date')
    op.drop_index('ix_task_tags')
    op.drop_index('ix_task_priority')

    # Drop columns
    op.drop_column('task', 'reminder_enabled')
    op.drop_column('task', 'recurrence_rule')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'tags')
    op.drop_column('task', 'priority')