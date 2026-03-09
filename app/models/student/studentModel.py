import uuid
from sqlalchemy import String, Integer, ForeignKey,UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user.userModel import User

from app.db.base import Base


class Student(Base):
    __tablename__ = "student"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False
    )

    mess_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    roll_number: Mapped[str] = mapped_column(String,unique=True,nullable=False )
    branch: Mapped[str] = mapped_column(String, nullable=False)
    batch: Mapped[int] = mapped_column(Integer, nullable=False)
    user: Mapped["User"] = relationship(back_populates="student")

    __table_args__ = (
        UniqueConstraint("user_id", name="unique_student_per_mess"),
    )
