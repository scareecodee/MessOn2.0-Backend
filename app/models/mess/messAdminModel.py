import uuid
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base   # <-- IMPORTANT

class MessAdmin(Base):
    __tablename__ = "mess_admin"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    google_sub = Column(String, unique=True, index=True, nullable=True)
    picture = Column(String, nullable=True)
