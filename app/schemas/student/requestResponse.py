from pydantic import BaseModel, EmailStr
from typing import List

class StudentResponse(BaseModel):
    name: str
    roll_number: str
    email: EmailStr
    branch:str
    batch: int
    isActive: bool
    picture:str|None

    class Config:
        from_attributes = True

class StudentCreate(StudentResponse):
    pass

class AddManuallyConflictResponse(BaseModel):
    email: EmailStr
    roll_number: str
    message:str

class AddStudentManuallyResponse(BaseModel):
    status:bool
    conflicts:List[AddManuallyConflictResponse]