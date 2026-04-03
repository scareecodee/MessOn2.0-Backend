from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.mess.messClosureModel import MessClosure
from uuid import UUID

from app.schemas.mess.messClosureSchema import MessClosureResponse


async def is_mess_closed(
    db: AsyncSession,
    mess_id: UUID,
    target_date: date
) -> bool:

    result = await db.execute(
        select(MessClosure).filter(
            MessClosure.mess_id == mess_id,
            MessClosure.start_date <= target_date,
            MessClosure.end_date >= target_date
        )
    )
    return result.scalar_one_or_none() is not None


async def get_closure_for_date(
    db: AsyncSession,
    mess_id: UUID,
    target_date: date
) -> MessClosure | None:

    result = await db.execute(
        select(MessClosure).filter(
            MessClosure.mess_id == mess_id,
            MessClosure.start_date <= target_date,
            MessClosure.end_date >= target_date
        )
    )
    return result.scalar_one_or_none()


async def get_all_closures(
    db: AsyncSession,
    mess_id: UUID
) -> list[MessClosureResponse]:

    result = await db.execute(
        select(MessClosure).filter(
            MessClosure.mess_id == mess_id
        ).order_by(MessClosure.start_date.asc())
    )
    return result.scalars().all()

async def check_closure_overlap(
        db: AsyncSession,
        mess_id: UUID,
        start_date,
        end_date,
        exclude_id: UUID | None = None
    ):
        query = select(MessClosure).where(
            MessClosure.mess_id == mess_id,
            and_(
                MessClosure.start_date <= end_date,
                MessClosure.end_date >= start_date
            )
        )

        if exclude_id:
            query = query.where(MessClosure.id != exclude_id)

        result = await db.execute(query)
        overlap = result.scalar_one_or_none()

        if overlap:
            raise HTTPException(
                status_code=400,
                detail="Closure dates overlap with existing closure"
            )