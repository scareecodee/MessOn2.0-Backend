from sqlalchemy import Column, String, Text, DateTime, Enum, UniqueConstraint, Boolean
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType
import uuid


class Menu(Base):
    __tablename__ = "menus"

    __table_args__ = (
        UniqueConstraint(
            "day",
            "meal_slot",
            "meal_type",
            name="uq_day_slot_type"
        ),
    )

    menu_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    day = Column(String(20), nullable=False, index=True)

    meal_slot = Column(
        Enum(MealSlot),
        nullable=False,
        index=True
    )

    meal_type = Column(
        Enum(MealType),
        nullable=False,
        index=True
    )

    menu_text = Column(Text, nullable=False)

    is_available = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
