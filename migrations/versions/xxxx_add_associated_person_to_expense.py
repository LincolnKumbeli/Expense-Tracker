"""Add associated_person to Expense

Revision ID: xxxx
Revises: None
Create Date: 2025-01-16 10:38:26.005631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'xxxx'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('expenses', sa.Column('associated_person', sa.String(length=256), nullable=True))


def downgrade():
    op.drop_column('expenses', 'associated_person')
