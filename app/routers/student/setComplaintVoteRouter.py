from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.schemas.student.complaintSchema import ComplaintVoteResponse,ComplaintVoteRequest
from app.services.complaintService import  set_complaint_vote_service

router=APIRouter(
    prefix="",
    tags=["Complaint and Feedback Section"],
)


@router.post(
    "/complaints/vote",
    response_model=ComplaintVoteResponse
)
async def set_complaint_vote(
    payload: ComplaintVoteRequest,
    current_user: User = Depends(get_current_role([UserRole.student])),
    db: AsyncSession = Depends(get_db)
):

    return await  set_complaint_vote_service(
        db=db,
        current_user=current_user,
        payload=payload
    )