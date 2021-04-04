"""agrego itk en la tabla sell

Revision ID: f2cd03a851b8
Revises: 14302aaa0290
Create Date: 2021-03-12 19:23:39.160437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2cd03a851b8'
down_revision = '14302aaa0290'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sell', sa.Column('estado', sa.Integer))

def downgrade():
    pass
