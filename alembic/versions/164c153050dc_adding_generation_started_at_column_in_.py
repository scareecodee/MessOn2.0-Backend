"""adding generation_started_at column in mess_weeks model

Revision ID: 164c153050dc
Revises: 387d7e9cd297
Create Date: 2026-03-27 19:36:25.827424

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '164c153050dc'
down_revision: Union[str, Sequence[str], None] = '387d7e9cd297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "mess_weeks",
        sa.Column("generation_started_at", sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    op.drop_column("mess_weeks", "generation_started_at")
