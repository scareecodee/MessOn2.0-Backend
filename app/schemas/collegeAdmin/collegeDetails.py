from uuid import UUID

from pydantic import BaseModel


class CollegeDetails(BaseModel):
    college_id: UUID
    college_name: str