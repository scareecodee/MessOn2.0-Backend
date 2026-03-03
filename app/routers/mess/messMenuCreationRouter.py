# @router.post("/create", response_model=MenuResponse)
# def create_menu(
#     payload: MenuCreate,
#     db: Session = Depends(get_db),
# ):
#     day = payload.day.lower()
#
#     existing = db.query(Menu).filter(
#         Menu.day == day,
#         Menu.meal_slot == payload.meal_slot,
#         Menu.meal_type == payload.meal_type
#     ).first()
#
#     if existing:
#         raise HTTPException(
#             status_code=400,
#             detail="Menu already exists for this day, slot and type"
#         )
#
#     menu = Menu(
#         day=day,
#         meal_slot=payload.meal_slot,
#         meal_type=payload.meal_type,
#         menu_text=payload.menu_text,
#     )
#
#     db.add(menu)
#     db.commit()
#     db.refresh(menu)
#
#     return menu
