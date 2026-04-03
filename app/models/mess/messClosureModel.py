import uuid
from datetime import date as DateType
from sqlalchemy import Date, ForeignKey, String, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class MessClosure(Base):
    __tablename__ = "mess_closures"

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

    reason: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "end_date >= start_date",
            name="check_closure_end_after_start"
        ),
        Index("ix_closure_mess_dates", "mess_id", "start_date", "end_date"),
    )