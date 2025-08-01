"""Add created_by, updated_by to units and unit_users

Revision ID: d7c6775ccd30
Revises: 07c0bae200de
Create Date: 2025-07-25 11:33:33.209392

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd7c6775ccd30'
down_revision = '07c0bae200de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('unit', sa.Column('created_by', sa.Uuid(), nullable=False))
    op.create_foreign_key(None, 'unit', 'user', ['created_by'], ['id'])
    op.add_column('unit_user', sa.Column('updated_by', sa.Uuid(), nullable=False))
    op.create_foreign_key(None, 'unit_user', 'user', ['updated_by'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'unit_user', type_='foreignkey')
    op.drop_column('unit_user', 'updated_by')
    op.drop_constraint(None, 'unit', type_='foreignkey')
    op.drop_column('unit', 'created_by')
    # ### end Alembic commands ###
