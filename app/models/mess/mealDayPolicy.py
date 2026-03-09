from sqlalchemy import Enum, Integer, ForeignKey,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.utils.weekDay import WeekDay
from app.utils.menuWeek import MenuWeek

from app.db.base import Base

class MessDayPolicy(Base):
    __tablename__ = "mess_day_policies"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    college_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        index=True
    )

    mess_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("messes.id", ondelete="CASCADE"),
        index=True
    )

    day: Mapped[WeekDay] = mapped_column(
        Enum(WeekDay, name="weekday_enum"),
        nullable=False
    )

    menu_week: Mapped[MenuWeek] = mapped_column(
        Enum(MenuWeek, name="menu_week_enum"),
        nullable=False
    )

    is_compulsory: Mapped[bool] = mapped_column(default=True,nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "mess_id",
            "menu_week",
            "day",
            name="unique_day_policy"
        ),
    )