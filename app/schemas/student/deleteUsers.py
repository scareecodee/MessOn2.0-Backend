from typing import List
from uuid import UUID
from app.utils.userRole import UserRole

from pydantic import BaseModel

class DeleteUsers(BaseModel):
    role: UserRole
    users_id : List[UUID]