from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.db.session import get_db
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.mess.messClosureSchema import MessClosureRequest, MessClosureResponse, MessClosureUpdateRequest
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.messClosureModel import MessClosure
from app.services.messClosureService import check_closure_overlap

router = APIRouter(
    prefix="/update",
    tags=["Mess Closure"],
)

@router.patch("/mess-closures/{mess_id}", status_code=200)
async def update_mess_closure(
    mess_id: UUID,
    payload: MessClosureUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_role([UserRole.college_admin])),
):

    # mess_admin = await db.execute(
    #     select(MessAdmin).filter(
    #         MessAdmin.user_id == current_user.id,
    #         MessAdmin.college_id == current_user.college_id
    #     )
    # )
    # mess_admin = mess_admin.scalar_one_or_none()
    #
    # if not mess_admin:
    #     raise HTTPException(404, "Mess admin not found")

    result = await db.execute(
        select(MessClosure).where(
            MessClosure.id == payload.closure_id,
            MessClosure.college_id == current_user.college_id,
            MessClosure.mess_id == mess_id
        )
    )
    closure = result.scalar_one_or_none()

    if not closure:
        raise HTTPException(status_code=404, detail="Closure not found")

    if payload.start_date is not None:
        closure.start_date = payload.start_date

    if payload.end_date is not None:
        closure.end_date = payload.end_date

    if payload.reason is not None:
        closure.reason = payload.reason

    if closure.end_date < closure.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")


    overlap_closure = await check_closure_overlap(
        db,
        mess_id,
        payload.start_date,
        payload.end_date,
        payload.closure_id,
    )
    if overlap_closure:
        raise HTTPException(404, "Mess closure overlap with other dates")

    await db.commit()
    await db.refresh(closure)

    return MessClosureResponse(
        closure_id=payload.closure_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
    )