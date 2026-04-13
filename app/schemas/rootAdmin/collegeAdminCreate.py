from uuid import UUID

from pydantic import BaseModel, EmailStr


class CollegeAdminCreate(BaseModel):
    name: str
    email: EmailStr
    college_id: UUID