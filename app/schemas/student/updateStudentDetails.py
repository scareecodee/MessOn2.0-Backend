from uuid import UUID

from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentUpdateRequest(BaseModel):
    name: Optional[str] | None = None
    roll_number: Optional[str] | None = None
    branch: Optional[str] | None = None
    batch: Optional[int] | None = None
    is_active: Optional[bool] | None = None
    email: Optional[EmailStr] | None = None
    picture: Optional[str] | None = None

class StudentDetailResponse(BaseModel):
    student_uuid: UUID
    name: str
    roll_number: str
    email: EmailStr
    branch:str
    batch: int
    is_active: bool
    picture: Optional[str] | None = None

class StudentUpdateConflictResponse(BaseModel):
    email: EmailStr
    roll_number: str
    message:str

class StudentUpdateResponse(BaseModel):
    status:bool
    student_details: StudentDetailResponse | None
    conflicts:StudentUpdateConflictResponse|None