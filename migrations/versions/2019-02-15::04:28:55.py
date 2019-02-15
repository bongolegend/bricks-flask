"""empty message

Revision ID: af6a3f50b8c5
Revises: 67c1c289692e
Create Date: 2019-02-15 04:28:55.167967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af6a3f50b8c5'
down_revision = '67c1c289692e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("task", "due_date",
        type_ = sa.types.DateTime(timezone=True))

def downgrade():
        op.alter_column("task", "due_date",
        type_ = sa.types.DateTime(timezone=False))
