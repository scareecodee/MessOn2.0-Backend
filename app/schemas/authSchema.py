from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., description="Google OAuth ID token")


class UserResponse(BaseModel):
    email: EmailStr
    name: str
    picture: str | None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserResponse
