from pydantic import BaseModel, Field
from typing import Optional


class StudentFilterParams(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(10, ge=1, le=50)
    search: Optional[str] = None
    # batch: Optional[int] = None