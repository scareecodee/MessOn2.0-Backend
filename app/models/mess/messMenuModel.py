from sqlalchemy import Column, String, Text, DateTime, Enum, UniqueConstraint, Boolean,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.utils.menuWeek import MenuWeek
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
from app.utils.weekDay import WeekDay
import uuid


class Menu(Base):
    __tablename__ = "menus"

    id : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id",
        ondelete="CASCADE"),nullable=False,index=True
    )


    day: Mapped[WeekDay] = mapped_column(Enum(WeekDay), nullable=False, index=True)

    meal_slot:Mapped[MealSlot]= mapped_column(Enum(MealSlot), nullable=False, index=True)

    meal_type:Mapped[MealType] = mapped_column(
        Enum(MealType),
        nullable=False,
        index=True
    )

    dishes:Mapped[str]=mapped_column(String, nullable=False)

    menu_week:Mapped[MenuWeek]= mapped_column(Enum(MenuWeek), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint(
            "mess_id",
            "day",
            "meal_slot",
            "meal_type",
            "menu_week",
            name="unique_menu_per_slot"
        ),
    )