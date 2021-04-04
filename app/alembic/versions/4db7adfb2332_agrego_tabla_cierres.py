"""agrego tabla cierres

Revision ID: 4db7adfb2332
Revises: b073652f2dc8
Create Date: 2021-03-17 12:20:16.609078

"""
from alembic import op
import sqlalchemy as sa
from db.models.qvariantalchemy import String, Integer, Boolean, DateTime, Enum
from db.models.sqlitedecimal import SqliteDecimal

# revision identifiers, used by Alembic.
revision = '4db7adfb2332'
down_revision = 'b073652f2dc8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sell', sa.Column('cierre_id', sa.Integer))
    op.create_table(
        'cierre',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', DateTime(timezone=True), server_default=sa.sql.func.now()),
    )


def downgrade():
    pass
