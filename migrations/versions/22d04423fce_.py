"""empty message

Revision ID: 22d04423fce
Revises: 22ee37bebfb6
Create Date: 2014-02-12 20:48:45.879463

"""

# revision identifiers, used by Alembic.
revision = '22d04423fce'
down_revision = '22ee37bebfb6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bimimage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('img_filename', sa.String(length=60), nullable=True),
    sa.Column('report_date', sa.String(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('report_date')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bimimage')
    ### end Alembic commands ###