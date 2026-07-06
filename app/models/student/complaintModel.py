import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user.userModel import User
from app.utils.complaintStatusEnum import ComplaintStatusEnum
from sqlalchemy import Enum
from app.db.base import Base


class Complaints(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
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

    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    likes_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    dislikes_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    complaint_status: Mapped[ComplaintStatusEnum] = mapped_column(
        Enum(
            ComplaintStatusEnum,
            name="complaint_status_enum"
        ),
        default=ComplaintStatusEnum.pending,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user = relationship("User")

    __table_args__ = (
        Index(
            "idx_complaints_listing",
            "complaint_status",
            "created_at",
            "likes_count"
        ),
    )