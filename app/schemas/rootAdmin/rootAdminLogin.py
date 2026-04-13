from pydantic import BaseModel


class RootAdminLoginRequest(BaseModel):
    email: str
    password: str