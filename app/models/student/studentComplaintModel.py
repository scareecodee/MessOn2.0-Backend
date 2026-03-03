from sqlalchemy import Column,Integer,Text,DateTime,ForeignKey,Boolean
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID

class Feedback(Base):
    __tablename__ = "Feedback"

    complainId = Column(Integer, primary_key=True, index=True)
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id"),
        nullable=False,
    )
    rating=Column(Integer)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    reply=Column(Text)
    likes=Column(Integer)
    dislikes=Column(Integer)
