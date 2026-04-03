"""creating pgcrypto extension

Revision ID: 387d7e9cd297
Revises: 0a31e20abc15
Create Date: 2026-03-27 19:32:45.016107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '387d7e9cd297'
down_revision: Union[str, Sequence[str], None] = '0a31e20abc15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() :
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")




def downgrade() :
    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
