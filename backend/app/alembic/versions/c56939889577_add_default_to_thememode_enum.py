from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c56939889577'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None

# Enums
thememode_enum = sa.Enum('default', 'light', 'dark', name='thememode')
lang_enum = sa.Enum('en', 'vi', name='lang')

def upgrade():
    # 1. Tạo ENUM types
    thememode_enum.create(op.get_bind(), checkfirst=True)
    lang_enum.create(op.get_bind(), checkfirst=True)

    # 2. Cập nhật bảng user
    op.alter_column('user', 'is_superuser',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    op.add_column('user', sa.Column('themes_mode', thememode_enum, nullable=True))
    op.add_column('user', sa.Column('lang', lang_enum, nullable=True))

def downgrade():
    op.drop_column('user', 'themes_mode')
    op.drop_column('user', 'lang')

    thememode_enum.drop(op.get_bind(), checkfirst=True)
    lang_enum.drop(op.get_bind(), checkfirst=True)

    op.alter_column('user', 'is_superuser',
               existing_type=sa.BOOLEAN(),
               nullable=True)
