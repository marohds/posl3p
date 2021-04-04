"""agrego total_venta y total_dto en la tabla sell

Revision ID: 996bbd31e50c
Revises: f2cd03a851b8
Create Date: 2021-03-12 19:37:02.412001

"""
from alembic import op
import sqlalchemy as sa
from db.models.sqlitedecimal import SqliteDecimal

# revision identifiers, used by Alembic.
revision = '996bbd31e50c'
down_revision = 'f2cd03a851b8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sell', sa.Column('total_venta', SqliteDecimal(2)))
    op.add_column('sell', sa.Column('total_dto', SqliteDecimal(2)))


def downgrade():
    pass
