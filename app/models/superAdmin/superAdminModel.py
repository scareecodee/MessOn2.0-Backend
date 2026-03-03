import uuid
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base   # <-- IMPORTANT

class SuperAdmin(Base):
    __tablename__ = "super_admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False, default="super_admin")
    google_sub = Column(String, unique=True, index=True, nullable=True)
    picture = Column(String, nullable=True)
