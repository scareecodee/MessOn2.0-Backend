import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StudentImportSession(Base):
    __tablename__ = "student_import_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    admin_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    to_insert: Mapped[dict] = mapped_column(JSON, nullable=False)

    to_update: Mapped[dict] = mapped_column(JSON, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
    )