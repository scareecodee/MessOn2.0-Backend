from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.utils.userRole import UserRole
from app.security.dependencies.getCurrentRole import get_current_role
from app.schemas.mess.messClosureSchema import  MessClosureResponse
from app.models.mess.messAdmin import MessAdmin
from app.models.mess.messClosureModel import MessClosure
from app.models.college.collegeAdmin import CollegeAdmin

router = APIRouter(
    prefix="/fetch",
    tags=["Mess Closure"],
)

@router.get("/mess-closures/{mess_id}",response_model=List[MessClosureResponse])
async def get_mess_closures(
    mess_id : UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_role([UserRole.college_admin])),
):




    result = await db.execute(
        select(MessClosure)
        .where(
            MessClosure.mess_id == mess_id,
            MessClosure.college_id == current_user.college_id
        )
        .order_by(MessClosure.start_date)
    )

    closures = result.scalars().all()

    return [MessClosureResponse(
        closure_id=closure.mess_id,
        start_date=closure.start_date,
        end_date=closure.end_date,
        reason=closure.reason

    )
          for closure in closures

    ]