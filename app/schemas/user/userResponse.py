from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserResponse(BaseModel):
    # id: UUID
    email: EmailStr
    name: str
    is_active: bool
    # picture :Optional[str] | None

    model_config = ConfigDict(from_attributes=True)