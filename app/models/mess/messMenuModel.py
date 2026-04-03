import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.enums import meal_slot_enum, meal_type_enum, weekday_enum, menu_week_enum
from app.utils.weekDays import WeekDays
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.menuWeek import MenuWeek


# from app.utils.menuWeek import MenuWeek  # kept for reference


class Menu(Base):
    __tablename__ = "mess_menu"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
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
    #
    week_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # menu_week: Mapped[MenuWeek] = mapped_column(
    #     menu_week_enum,
    #     nullable=False
    # )

    day: Mapped[WeekDays] = mapped_column(
        weekday_enum,
        nullable=False,
        index=True
    )

    meal_slot: Mapped[MealSlot] = mapped_column(
        meal_slot_enum,
        nullable=False,
        index=True
    )

    meal_type: Mapped[MealType] = mapped_column(
        meal_type_enum,
        nullable=False,
        index=True
    )

    dishes: Mapped[str] = mapped_column(String, nullable=False)

    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "mess_id", "day", "meal_slot", "meal_type", "week_id",
            name="unique_menu_per_slot"
        ),

    #     Index(
    #         "ix_menu_lookup",
    #         "mess_id", "week_id", "day"
    #     ),
    )