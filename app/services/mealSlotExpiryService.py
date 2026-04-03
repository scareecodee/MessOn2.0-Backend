# app/services/meal_slot_expiry_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.mess.mealSlotExpiryModel import MealSlotExpiry
from app.schemas.mess.mealSlotExpirySchema import MealSlotExpiryRequest


async def upsert_meal_slot_expiry(
    db: AsyncSession,
    data: list[MealSlotExpiryRequest],
    mess_id,
    college_id
):
    for item in data:
        stmt = insert(MealSlotExpiry).values(
            mess_id=mess_id,
            college_id=college_id,
            meal_slot=item.meal_slot,
            start_time=item.start_time,
            end_time=item.end_time
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["mess_id", "meal_slot"],
            set_={
                "start_time": stmt.excluded.start_time,
                "end_time": stmt.excluded.end_time,
            }
        )

        await db.execute(stmt)

    await db.commit()

    return True