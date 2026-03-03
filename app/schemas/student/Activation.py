from pydantic import BaseModel

class Toggle(BaseModel):
    is_active: bool = True