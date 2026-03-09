from pydantic import BaseModel

class MessCreate(BaseModel):
    name: str
    location: str
    is_active: bool=True