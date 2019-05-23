"""empty message

Revision ID: 9565e668b0c3
Revises: 
Create Date: 2019-05-23 10:51:12.157956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9565e668b0c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('army',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('number_squads', sa.Integer(), nullable=True),
    sa.Column('webhook_url', sa.String(length=120), nullable=True),
    sa.Column('access_token', sa.String(length=120), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('join_type', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('access_token')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('army')
    # ### end Alembic commands ###