"""Create tag tables

Revision ID: 002
Revises: 001
Create Date: 2026-02-03 11:05:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create tag table
    op.create_table('tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for tag table
    op.create_index('ix_tag_user_id', 'tag', ['user_id'])
    op.create_index('ix_tag_name', 'tag', ['name'])

    # Create task_tags association table
    op.create_table('task_tags',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'tag_id')
    )


def downgrade():
    # Drop task_tags association table
    op.drop_table('task_tags')

    # Drop tag table
    op.drop_index('ix_tag_name')
    op.drop_index('ix_tag_user_id')
    op.drop_table('tag')