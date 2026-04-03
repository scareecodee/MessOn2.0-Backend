import uuid
from datetime import date as DateType
from sqlalchemy import ForeignKey, UniqueConstraint, Date, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.enums import meal_slot_enum, meal_type_enum
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType

# from app.utils.menuWeek import MenuWeek  # kept for reference
# from app.utils.weekDay import WeekDays   # kept for reference


class MealPreference(Base):
    __tablename__ = "meal_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # date-based — replaces week_id + day
    # week_id: Mapped[uuid.UUID] = mapped_column(
    #     UUID(as_uuid=True),
    #     ForeignKey("mess_weeks.id", ondelete="CASCADE"),
    #     nullable=False,
    #     index=True
    # )
    # day: Mapped[WeekDays] = mapped_column(weekday_enum, nullable=False)

    date: Mapped[DateType] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    meal_slot: Mapped[MealSlot] = mapped_column(
        meal_slot_enum,
        nullable=False
    )

    # nullable=True — None means optional day, no preference submitted
    meal_type: Mapped[MealType | None] = mapped_column(
        meal_type_enum,
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id", "date", "meal_slot",
            name="unique_preference_per_student_date_slot"
        ),
        Index("ix_pref_mess_date", "mess_id", "date"),
    )