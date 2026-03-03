import uuid
from sqlalchemy import Column, String, Date, Enum, DateTime, ForeignKey,UniqueConstraint,Boolean,BigInteger
from app.db.base import Base
from datetime import date as DateType
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.utils.mealType import MealType
from app.utils.mealSlot import MealSlot


class Coupon(Base):
    __tablename__ = "coupons"

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "date",
            "mealSlot",
            name="uq_user_day_meal",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    userId: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
        index=True,
    )

    date: Mapped[DateType] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    mealSlot:Mapped[MealSlot]=mapped_column(
        Enum(MealSlot),
        nullable=False,
        index=True,
    )

    mealType: Mapped[MealType] = mapped_column(
        Enum(MealType),
        nullable=False,
        index=True,       
    )

    expiresAt: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    usedAt: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,          
    )

