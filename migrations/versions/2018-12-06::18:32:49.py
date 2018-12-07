"""empty message

Revision ID: c0fb5f5a5950
Revises: 95b142a7d473
Create Date: 2018-12-06 18:32:49.137223

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0fb5f5a5950'
down_revision = '95b142a7d473'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('exchange', 'inbound', type_=sa.String(length=612))
    op.alter_column('exchange', 'outbound', type_=sa.String(length=612))


def downgrade():
    op.alter_column('exchange', 'inbound', type_=sa.String(length=256))
    op.alter_column('exchange', 'outbound', type_=sa.String(length=256))
