"""create audit_log table

Revision ID: 702c094a00b6
Revises: 6da033f0f2fb
Create Date: 2025-07-25 17:48:09.878565

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '702c094a00b6'
down_revision = '6da033f0f2fb'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
