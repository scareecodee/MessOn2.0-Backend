from sqlalchemy import (
    Date, Integer, ForeignKey,
    CheckConstraint, UniqueConstraint, Index,DateTime
)
from datetime import datetime,timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import mapped_column, Mapped

from app.db.enums import meal_slot_enum, meal_type_enum
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.db.base import Base


class Rating(Base):
    __tablename__ = "ratings"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())

    student_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

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

    meal_type: Mapped[MealType] = mapped_column(
        meal_type_enum,
        nullable=False
    )

    rating = mapped_column(Integer, nullable=False)

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
            "student_id", "date", "meal_slot", "meal_type",
            name="uq_student_meal_rating"
        ),

        CheckConstraint("rating BETWEEN 1 AND 5", name="check_rating_range"),

        Index(
            "idx_rating_aggregation",
            "mess_id", "college_id", "date", "meal_slot"
        ),
    )