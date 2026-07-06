from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from app.utils.complaintStatusEnum import ComplaintStatusEnum
from app.utils.complaintVoteTypeEnum import ComplaintVoteTypeEnum

class CreateComplaintRequest(BaseModel):
    subject:str
    description:str


class ComplaintResponse(BaseModel):
    complaint_id: UUID
    student_name: str
    student_roll_number: str
    subject: str
    description: str
    likes_count: int
    dislikes_count: int
    complaint_status: ComplaintStatusEnum
    created_at: datetime
    user_vote: ComplaintVoteTypeEnum | None
    


class ComplaintListResponse(BaseModel):
    complaints: list[ComplaintResponse]
    next_cursor: str | None


class ComplaintVoteRequest(BaseModel):
    complaint_id: UUID
    vote_type: ComplaintVoteTypeEnum

class ComplaintVoteResponse(BaseModel):
    likes_count: int
    dislikes_count: int
    user_vote: ComplaintVoteTypeEnum | None