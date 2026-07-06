import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.user.userModel import User
from sqlalchemy import Enum
from app.utils.complaintVoteTypeEnum import ComplaintVoteTypeEnum
from app.db.base import Base

class ComplaintVote(Base):
    __tablename__ = "complaint_votes"

    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("complaints.id", ondelete="CASCADE"),
        primary_key=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )

    vote_type: Mapped[ComplaintVoteTypeEnum] = mapped_column(
        Enum(ComplaintVoteTypeEnum),
        nullable=False
    )