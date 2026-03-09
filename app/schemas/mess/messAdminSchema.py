from uuid import UUID
from pydantic import BaseModel, EmailStr


class MessAdminUpdate(BaseModel):
    email:str | None = None
    name: str | None = None
    is_active: bool | None = None

class MessAdminResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    is_active: bool
    google_sub: str | None
    picture: str | None

    class Config:
        from_attributes = True

    
