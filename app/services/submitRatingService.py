from fastapi import HTTPException
from datetime import date as dt_date

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

    await update_summary_logic(
        db,
        mess_id=result["mess_id"],
        college_id=result["college_id"],
        date=date,
        meal_slot=meal_slot,
        meal_type=result["meal_type"],
        rating=rating
    )


    return {
        "message": "Rating submitted successfully"
    }