"""create post table

Revision ID: 591b75277948
Revises: 
Create Date: 2022-10-25 19:05:22.909399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '591b75277948'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("posts", sa.Column("id", sa.Integer, primary_key=True), sa.Column(
        "title", sa.String, nullable=False))
    pass


def downgrade() -> None:
    op.drop_table("posts")
    pass
