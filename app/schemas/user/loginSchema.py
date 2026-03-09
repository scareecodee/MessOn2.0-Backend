from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth ID token")
    role: str
    college_id:UUID


class UserInfo(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    picture :Optional[str] | None

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserInfo
