from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID

class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth ID token")


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    picture: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
