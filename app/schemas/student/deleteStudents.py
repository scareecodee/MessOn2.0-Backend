from typing import List
from uuid import UUID

from pydantic import BaseModel


class DeleteStudents(BaseModel):
    students_id: List[UUID]