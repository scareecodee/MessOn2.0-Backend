from pydantic import BaseModel
from datetime import datetime

class NotificationCreate(BaseModel):
    subject: str
    description: str


class NotificationResponse(BaseModel):
    id: int
    subject: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
