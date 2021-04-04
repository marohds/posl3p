"""agrego descuento en la tabla sell_item

Revision ID: b073652f2dc8
Revises: 996bbd31e50c
Create Date: 2021-03-12 20:32:25.333531

"""
from alembic import op
import sqlalchemy as sa
from db.models.sqlitedecimal import SqliteDecimal

# revision identifiers, used by Alembic.
revision = 'b073652f2dc8'
down_revision = '996bbd31e50c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sell_item', sa.Column('descuento', SqliteDecimal(2)))


def downgrade():
    pass
