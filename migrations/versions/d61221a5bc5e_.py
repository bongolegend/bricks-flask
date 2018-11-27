"""empty message

Revision ID: d61221a5bc5e
Revises: 
Create Date: 2018-11-23 14:08:27.203773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd61221a5bc5e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('phone_number', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_table('notification',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tag', sa.String(length=32), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('trigger_type', sa.String(length=32), nullable=False),
    sa.Column('day_of_week', sa.String(length=32), nullable=True),
    sa.Column('hour', sa.Integer(), nullable=False),
    sa.Column('minute', sa.Integer(), nullable=False),
    sa.Column('jitter', sa.Integer(), nullable=True),
    sa.Column('end_date', sa.DateTime(), nullable=True),
    sa.Column('timezone', sa.String(length=32), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    op.drop_table('user')
    # ### end Alembic commands ###