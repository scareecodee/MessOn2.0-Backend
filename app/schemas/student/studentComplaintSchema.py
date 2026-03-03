from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CreateComplaint(BaseModel):
    complaint_type: str
    description: str

class ComplaintRegistered(BaseModel):
    registered:bool

class ComplaintResponse(BaseModel):
    complaint_id: int
    student_id:UUID
    subject: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
