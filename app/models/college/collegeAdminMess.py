from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CollegeAdminMess(Base):
    __tablename__ = "college_admin_mess"

    admin_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("college_admin.id", ondelete="CASCADE"),
        nullable=False
    )

    mess_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mess.id", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        PrimaryKeyConstraint("admin_id", "mess_id"),
    )