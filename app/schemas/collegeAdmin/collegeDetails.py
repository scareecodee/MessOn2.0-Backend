from pydantic import BaseModel


class CollegeDetails(BaseModel):
    college_id: str
    college_name: str