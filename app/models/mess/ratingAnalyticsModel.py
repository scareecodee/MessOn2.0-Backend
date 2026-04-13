from datetime import datetime

from sqlalchemy import (
    Date, ForeignKey,
    UniqueConstraint, Index, Float, Integer, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped

from app.db.base import Base
from app.db.enums import meal_slot_enum
from app.utils.mealSlot import MealSlot


class RatingAnalytics(Base):
    __tablename__ = "rating_analytics"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())


    mess_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    college_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )


    date = mapped_column(Date, nullable=False, index=True)

    meal_slot: Mapped[MealSlot] = mapped_column(
        meal_slot_enum,
        nullable=False,
        index=True
    )

    veg_sum = mapped_column(Integer, nullable=True)
    veg_count = mapped_column(Integer, nullable=True)

    non_veg_sum = mapped_column(Integer, nullable=True)
    non_veg_count = mapped_column(Integer, nullable=True)

    total_sum = mapped_column(Integer, nullable=True)
    total_count = mapped_column(Integer, nullable=True)


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "mess_id", "date", "meal_slot",
            name="uq_rating_analytics_slot"
        ),

        Index(
            "idx_rating_analytics_lookup",
            "mess_id", "date", "meal_slot"
        ),
    )