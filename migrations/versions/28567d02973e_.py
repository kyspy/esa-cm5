"""empty message

Revision ID: 28567d02973e
Revises: 16e8155c3458
Create Date: 2014-02-25 15:25:03.685418

"""

# revision identifiers, used by Alembic.
revision = '28567d02973e'
down_revision = '16e8155c3458'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('baseline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('early', sa.Integer(), nullable=True),
    sa.Column('late', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('baseline')
    ### end Alembic commands ###