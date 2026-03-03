import uuid
from sqlalchemy import DateTime,Column, String, Integer, Boolean, DateTime, UUID,JSON
from app.db.base import Base
from sqlalchemy.sql import func

class StudentImportSession(Base):
    __tablename__ = "student_import_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), nullable=True)
    to_insert = Column(JSON, nullable=False)
    to_update = Column(JSON, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)

