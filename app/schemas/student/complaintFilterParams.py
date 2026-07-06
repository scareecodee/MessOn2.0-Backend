from typing import Optional
from pydantic import BaseModel, Field

from app.utils.complaintStatusEnum import ComplaintStatusEnum


class ComplaintFilterParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(10, ge=1, le=10)
    status: Optional[ComplaintStatusEnum] = None
    search: Optional[str] = None