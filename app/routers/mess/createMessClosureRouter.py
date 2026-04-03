from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.mess.messClosureSchema import MessClosureRequest,MessClosureResponse
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.messClosureModel import MessClosure
from app.services.messClosureService import check_closure_overlap
from app.models.college.collegeAdmin import CollegeAdmin

router = APIRouter(
    prefix="/create",
    tags=["Mess Closure"],
)

@router.post("/mess-closures/{mess_id}",response_model=MessClosureResponse)
async def update_mess_closure(
    mess_id: UUID,
    payload: MessClosureRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_role([UserRole.college_admin])),
):
    user = await db.execute(
        select(CollegeAdmin).filter(
            CollegeAdmin.id == current_user.id,
            CollegeAdmin.college_id == current_user.college_id
        )
    )
    college_admin = user.scalar_one_or_none()

    if not college_admin:
        raise HTTPException(404, "College Mess admin not found")

    overlap_closure = await check_closure_overlap(
        db,
        mess_id,
        payload.start_date,
        payload.end_date,
    )
    if overlap_closure:
        raise HTTPException(404, "Mess closure overlap with other dates")

    closure=(
        MessClosure(
            mess_id = mess_id,
            college_id = current_user.college_id,
            start_date = payload.start_date,
            end_date = payload.end_date,
            reason = payload.reason,
        )
    )

    db.add(closure)
    await db.flush()

    await db.commit()

    return MessClosureResponse(
        closure_id=closure.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
    )