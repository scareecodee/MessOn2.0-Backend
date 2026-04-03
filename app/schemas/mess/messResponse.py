from pydantic import BaseModel,ConfigDict
from uuid import UUID


class MessResponse(BaseModel):
    id:UUID
    name: str
    location: str
    is_active: bool=True

    model_config = ConfigDict(from_attributes=True)