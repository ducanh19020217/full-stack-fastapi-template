"""add logresultenum and status to audit_log

Revision ID: d0eea768f6d8
Revises: 2016cfc2c03e
Create Date: 2025-07-28 09:20:05.080474

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd0eea768f6d8'
down_revision = '2016cfc2c03e'
branch_labels = None
depends_on = None

# Enum định nghĩa giá trị
log_result_enum = sa.Enum('success', 'failed', name='logresultenum')

def upgrade():
    op.execute("ALTER TYPE logresult ADD VALUE IF NOT EXISTS 'success';")


def downgrade():
    pass
