"""add coupon  generation status column in mess_weeks table

Revision ID: 0a31e20abc15
Revises: ac404c2205cf
Create Date: 2026-03-20 12:00:38.670664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a31e20abc15'
down_revision: Union[str, Sequence[str], None] = 'ac404c2205cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "mess_weeks",
        sa.Column("coupon_generation_status", sa.String(), nullable=True)
    )

    op.execute(
        "UPDATE mess_weeks SET coupon_generation_status = 'pending'"
    )

    op.alter_column(
        "mess_weeks",
        "coupon_generation_status",
        server_default="pending"
    )


    op.create_check_constraint(
        "check_generation_status",
        "mess_weeks",
        "coupon_generation_status IN ('pending','generated','skipped','failed')"
    )

    op.alter_column(
        "mess_weeks",
        "coupon_generation_status",
        nullable=False
    )


def downgrade():
    op.drop_constraint("check_generation_status", "mess_weeks", type_="check")
    op.drop_column("mess_weeks", "coupon_generation_status")