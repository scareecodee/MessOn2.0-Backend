# app/models/meal_slot_expiry.py

import uuid
from sqlalchemy import ForeignKey, UniqueConstraint, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.enums import meal_slot_enum
from app.utils.mealSlot import MealSlot
from datetime import time


class MealSlotExpiry(Base):
    __tablename__ = "meal_slot_expiry"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    meal_slot: Mapped[MealSlot] = mapped_column(
        meal_slot_enum,
        nullable=False
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "mess_id", "meal_slot",
            name="unique_expiry_per_slot"
        ),
    )