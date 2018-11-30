"""empty message

Revision ID: d7643fd49475
Revises: 1d5597b918d2
Create Date: 2018-11-30 11:50:35.801360

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7643fd49475'
down_revision = '1d5597b918d2'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('exchange', 'inbound', type_=sa.String(length=256))
    op.alter_column('exchange', 'outbound', type_=sa.String(length=256))


def downgrade():
    op.alter_column('exchange', 'inbound', type_=sa.String(length=128))
    op.alter_column('exchange', 'outbound', type_=sa.String(length=128))
