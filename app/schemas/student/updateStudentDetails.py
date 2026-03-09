from pydantic import BaseModel, EmailStr
from typing import Optional

class StudentUpdateRequest(BaseModel):
    name: Optional[str] = None
    roll_number: Optional[str] = None
    branch: Optional[str] = None
    batch: Optional[int] = None
    is_active: Optional[bool] = None
    email: Optional[str] = None

class StudentResponse(BaseModel):
    name: str
    roll_number: str
    email: EmailStr
    branch:str
    batch: int
    is_active: bool

class StudentUpdateConflictResponse(BaseModel):
    email: EmailStr
    roll_number: str
    message:str

class StudentUpdateResponse(BaseModel):
    status:bool
    conflicts:StudentUpdateConflictResponse|None