"""Inicial

Revision ID: b6243625aa74
Revises: 
Create Date: 2021-03-12 15:03:07.441118

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from db.models.qvariantalchemy import String, Integer, Boolean, DateTime, Enum
from db.models.sqlitedecimal import SqliteDecimal
from db.models.objects import Venta


# revision identifiers, used by Alembic.
revision = 'b6243625aa74'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('sell', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    # op.add_column('product', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.sql.func.now(), nullable=True))
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for venta in session.query(Venta):
        venta.created_at = sa.sql.func.now()
    session.commit()

def downgrade():
    op.drop_column('sell', 'created_at')

