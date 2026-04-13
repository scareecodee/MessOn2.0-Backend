import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Enum, ForeignKey,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.utils.userRole import UserRole


class RootAdmin(Base):
    __tablename__ = "root_admins"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String,nullable=False)

    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    password : Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

