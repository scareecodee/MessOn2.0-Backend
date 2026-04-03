from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.schemas.user.createUser import UserCreate


class StudentCreate(UserCreate):
    roll_number: str
    branch:str
    batch: int



    class Config:
        from_attributes = True

class AddManuallyConflictResponse(BaseModel):
    email: EmailStr
    roll_number: str
    message:str

class AddStudentManuallyResponse(BaseModel):
    status:bool
    conflicts:List[AddManuallyConflictResponse]