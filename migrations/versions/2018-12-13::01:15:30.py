"""empty message

Revision ID: b9d4a43b7ab2
Revises: b423ea304fa4
Create Date: 2018-12-13 01:15:30.325123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9d4a43b7ab2'
down_revision = 'b423ea304fa4'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('exchange', 'confirmation',
            type_=sa.VARCHAR(length=128))


def downgrade():
    op.alter_column('exchange', 'confirmation',
        type_=sa.VARCHAR(length=64))
