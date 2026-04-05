import uuid
from datetime import datetime, date as DateType
from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.db.enums import meal_slot_enum, meal_type_enum
from app.utils.mealSlot import MealSlot
from app.utils.mealType import MealType


class Coupon(Base):
    __tablename__ = "coupons"

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
        nullable=False,
        index=True
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    week_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    date: Mapped[DateType] = mapped_column(
        Date,
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
        nullable=False
    )

    scanned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )

    scanned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint(
            "student_id", "date", "meal_slot",
            name="uq_student_date_meal_slot"
        ),

        Index("ix_coupon_student_date", "student_id", "date"),
        Index("ix_coupon_mess_date", "mess_id", "date"),
    )

    # CREATE
    # INDEX
    # idx_coupon_lookup
    # ON
    # coupons(student_id, mess_id, college_id, date, meal_slot);
