from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user.userModel import User
from app.security.dependencies.getCurrentUser import get_current_user

from app.models.student.studentModel import Student
from app.models.student.complaintModel import Complaints
from app.models.student.complaintVoteModel import ComplaintVote
from app.schemas.student.complaintSchema import ComplaintListResponse
from app.schemas.student.complaintFilterParams import  ComplaintFilterParams
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole

from app.services.complaintService import fetch_complaints

router=APIRouter(
    prefix="",
    tags=["Complaint and Feedback Section"],
)


@router.get(
    "/fetch-complaints",
    response_model=ComplaintListResponse
)
async def get_complaints(
    params: ComplaintFilterParams = Depends(),
    current_user: User = Depends(get_current_role([UserRole.college_admin,UserRole.mess_admin,UserRole.student])),
    db: AsyncSession = Depends(get_db)
):

    return await fetch_complaints(
        db=db,
        current_user=current_user,
        params=params
    )