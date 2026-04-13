from uuid import UUID

from pydantic import BaseModel, EmailStr

class CollegeCreate(BaseModel):
    name: str
    domain: str
