"""add page number

Revision ID: xxxx
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20240101_add_page_number"
down_revision = "61548e9a38c3"
branch_labels = None
depends_on = None


def upgrade():
    # Add page_number column
    op.add_column("cursor", sa.Column("page_number", sa.Integer(), nullable=True))

    # Populate page numbers for existing cursors
    conn = op.get_bind()
    cursors = conn.execute(sa.text("SELECT id FROM cursor ORDER BY created_at ASC")).fetchall()
    for i, cursor in enumerate(cursors, 1):
        conn.execute(
            sa.text("UPDATE cursor SET page_number = :page WHERE id = :id"),
            {"page": i, "id": cursor[0]},
        )


def downgrade():
    op.drop_column("cursor", "page_number")
