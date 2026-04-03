from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class StudentResponse(BaseModel):
    student_uuid:UUID
    name: str
    roll_number: str
    email: EmailStr
    branch: str
    batch: int
    is_active: bool
    picture: str | None

class StudentListResponse(BaseModel):
    students_list: list[StudentResponse]
    next_cursor: str | None

