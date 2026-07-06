from fastapi import Response
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.schemas.student.complaintSchema import ComplaintResponse,CreateComplaintRequest
from app.services.complaintService import create_complaint

router=APIRouter(
    prefix="",
    tags=["Complaint and Feedback Section"],
)

@router.post("/create-complaints",status_code=status.HTTP_201_CREATED)
async def create_complaint_route(
    payload: CreateComplaintRequest,
    current_user: User = Depends(get_current_role([UserRole.student])),
    db: AsyncSession = Depends(get_db)
):
    await create_complaint(
        db=db,
        current_user=current_user,
        payload=payload
    )

    return Response(
        status_code=status.HTTP_201_CREATED
    )

