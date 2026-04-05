import uuid
from datetime import date as DateType, datetime
from sqlalchemy import Date, ForeignKey, UniqueConstraint, CheckConstraint, Index, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class MessWeek(Base):
    __tablename__ = "mess_weeks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_date: Mapped[DateType] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[DateType] = mapped_column(
        Date,
        nullable=False
    )

    coupon_generation_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="pending"
    )
    coupon_generation_started_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )


    __table_args__ = (
        UniqueConstraint(
            "mess_id", "start_date",
            name="unique_week_per_mess"
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="check_end_after_start"
        ),
        Index("ix_mess_week_mess_dates", "mess_id", "start_date", "end_date"),
    )