"""adding ix_menu_lookup in mess_menu

Revision ID: b9fffe0bfcb4
Revises: 164c153050dc
Create Date: 2026-03-28 05:39:27.212473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9fffe0bfcb4'
down_revision: Union[str, Sequence[str], None] = '164c153050dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() :
    op.create_index(
        "ix_menu_lookup",
        "mess_menu",
        ["mess_id", "week_id", "day"]
    )


def downgrade() :
    op.drop_index("ix_menu_lookup", table_name="mess_menu")
