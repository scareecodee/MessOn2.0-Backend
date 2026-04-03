from sqlalchemy import Enum, Integer, ForeignKey,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.utils.weekDays import WeekDays
from app.utils.menuWeek import MenuWeek
import uuid

from app.db.base import Base

class MessDayPolicy(Base):
    __tablename__ = "mess_day_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    college_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        index=True
    )

    mess_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        index=True
    )

    day: Mapped[WeekDays] = mapped_column(
        Enum(WeekDays, name="weekday_enum"),
        nullable=False
    )

    week_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess_weeks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # menu_week: Mapped[MenuWeek] = mapped_column(
    #     Enum(MenuWeek, name="menu_week_enum"),
    #     nullable=False
    # )

    is_compulsory: Mapped[bool] = mapped_column(default=True,nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "mess_id",
            "week_id",
            "day",
            name="unique_day_policy"
        ),
    )