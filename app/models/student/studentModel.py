import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    name = Column(String, nullable=False)
    roll_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    branch = Column(String, nullable=False)
    batch=Column(Integer, nullable=False)
    hasReadNotifications = Column(Boolean, nullable=False, default=False)
    # is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    google_sub = Column(String, unique=True, index=True, nullable=True)
    picture = Column(String, nullable=True)