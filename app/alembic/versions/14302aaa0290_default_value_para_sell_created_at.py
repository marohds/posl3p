"""Default value para sell.created_at

Revision ID: 14302aaa0290
Revises: b6243625aa74
Create Date: 2021-03-12 15:49:02.874997

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14302aaa0290'
down_revision = 'b6243625aa74'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sell', schema=None) as batch_op:
        batch_op.alter_column('created_at', server_default=sa.sql.func.now())

    # op.add_column('product', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.sql.func.now(), nullable=True))

def downgrade():
    pass
