from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.mess.messMenuSchema import DayWiseMenuResponse
from app.models.mess.messMenuModel import Menu,MealType

router = APIRouter(
    prefix="/fetch/menu",
    tags=["Fetch Day-wise Menu"]
)

@router.get("/{day}", response_model=DayWiseMenuResponse)
def fetch_daywise(
    day: str,
    db: Session = Depends(get_db),
):
    day = day.lower()

    menus = db.query(Menu).filter(
        Menu.day == day,
        Menu.is_available == True
    ).all()

    if not menus:
        raise HTTPException(
            status_code=404,
            detail=f"No menu found for {day}"
        )

    response = DayWiseMenuResponse(
        breakfast={},
        lunch={},
        dinner={}
    )

    for menu in menus:
        slot_dict = getattr(response, menu.meal_slot.value)
        slot_dict[menu.meal_type.value] = menu

    return response
