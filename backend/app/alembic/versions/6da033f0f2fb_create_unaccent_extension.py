"""create unaccent extension

Revision ID: 6da033f0f2fb
Revises: 3fefe677d5cc
Create Date: 2025-07-25 17:30:29.905957

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '6da033f0f2fb'
down_revision = '3fefe677d5cc'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS unaccent")
