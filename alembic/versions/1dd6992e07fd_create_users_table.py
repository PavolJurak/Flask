"""Create users table

Revision ID: 1dd6992e07fd
Revises: 
Create Date: 2022-10-31 14:02:15.047820

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1dd6992e07fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, unique=True),
        sa.Column("password", sa.String))


def downgrade() -> None:
    op.drop_table("user")
