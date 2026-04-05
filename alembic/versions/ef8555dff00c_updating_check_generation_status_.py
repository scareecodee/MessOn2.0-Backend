"""updating check_generation_status constraint

Revision ID: ef8555dff00c
Revises: b9fffe0bfcb4
Create Date: 2026-03-28 06:55:02.849122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef8555dff00c'
down_revision: Union[str, Sequence[str], None] = 'b9fffe0bfcb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.drop_constraint(
        "check_generation_status",
        "mess_weeks",
        type_="check"
    )

    op.create_check_constraint(
        "check_generation_status",
        "mess_weeks",
        "coupon_generation_status IN ('pending','generating','generated','skipped','failed')"
    )


def downgrade():
    # revert back if needed
    op.drop_constraint(
        "check_generation_status",
        "mess_weeks",
        type_="check"
    )

    op.create_check_constraint(
        "check_generation_status",
        "mess_weeks",
        "coupon_generation_status IN ('pending','generated','skipped','failed')"
    )
