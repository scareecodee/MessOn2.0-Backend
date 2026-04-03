from app.utils.mealType import MealType

def get_default_meal(available_types):

    if MealType.veg in available_types:
        return MealType.veg

    return MealType.nonVeg