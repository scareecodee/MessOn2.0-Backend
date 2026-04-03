import uuid
from sqlalchemy import  ForeignKey, UniqueConstraint,String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.utils.weekDays import WeekDays
from app.db.enums import weekday_enum


class SubmissionWindowTemplate(Base):
    __tablename__ = "submission_window_templates"

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

    start_day: Mapped[WeekDays] = mapped_column(
        weekday_enum,
        nullable=False
    )

    end_day: Mapped[WeekDays] = mapped_column(
        weekday_enum,
        nullable=False
    )

    start_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False
    )

    end_time: Mapped[Time] = mapped_column(
        Time,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "mess_id",
            name="unique_window_per_mess"
        ),
    )
