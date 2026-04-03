"""creating roll,created,id index for pagination

Revision ID: ac404c2205cf
Revises: 
Create Date: 2026-03-04 16:30:15.930618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac404c2205cf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Enable trigram extension for fuzzy search
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS pg_trgm;
        """
    )

    # Trigram index for name search (ILIKE '%text%')
    op.execute("""
               CREATE INDEX IF NOT EXISTS idx_users_name_trgm
                   ON users
                   USING gin (name gin_trgm_ops);
               """)

    # Pagination index for cursor pagination
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_students_pagination
        ON students (roll_number, created_at DESC, user_id DESC);
        """
    )


def downgrade():
    # Drop pagination index
    op.execute(
        """
        DROP INDEX IF EXISTS idx_students_pagination;
        """
    )

    # Drop trigram index
    op.execute(
        """
        DROP INDEX IF EXISTS idx_students_name_trgm;
        """
    )
