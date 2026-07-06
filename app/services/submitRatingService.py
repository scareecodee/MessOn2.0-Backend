from fastapi import HTTPException
from datetime import date as dt_date
from fastapi import Response,status
from app.services.insertAndUpdateRatingService import update_summary_logic, insert_rating


async def submit_rating(
    db,
    student_id,
    date,
    meal_slot,
    rating
):

    if date != dt_date.today():
        raise HTTPException(400, "You can only rate today's meal")

    # async with db.begin():
    print("calling insert")

    result = await insert_rating(
        db,
        student_id,
        date,
        meal_slot,
        rating
    )

    if not result:
        raise HTTPException(
            400,
            "Rating not allowed or already submitted"
        )
    
    print("calling upsert")
    await update_summary_logic(
        db,
        mess_id=result["mess_id"],
        college_id=result["college_id"],
        date=date,
        meal_slot=meal_slot,
        meal_type=result["meal_type"],
        rating=rating
    )

    await db.commit()

    return Response(
        status_code=status.HTTP_201_CREATED
    )