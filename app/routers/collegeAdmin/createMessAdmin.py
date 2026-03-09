from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.models.mess.messAdmin import MessAdmin
from app.models.user.userModel import User
from app.models.mess.messModel import Mess
from app.schemas.user.createUser import UserCreate
from app.schemas.user.userResponse import UserResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole


router = APIRouter(
    prefix="/mess",
    tags=["Manage Mess"]
)

@router.post("/{mess_id}/admins", response_model=UserResponse)
def create_mess_admin(
    mess_id: UUID,
    payload: UserCreate,
    current_user: User = Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db)
):

    mess = (
        db.query(Mess)
        .filter(
            Mess.id == mess_id,
            Mess.college_id == current_user.college_id
        )
        .first()
    )

    if not mess:
        raise HTTPException(404, "Mess not found")

    user = db.query(User).filter(User.email == payload.email).first()

    #will have to check this if each email is unique then throw error on same email

    if user:

        if user.role in [UserRole.student, UserRole.college_admin]:
            raise HTTPException(
                status_code=400,
                detail="Email already belongs to a student or college admin"
            )

    else:

        # create new mess admin user
        user = User(
            college_id=current_user.college_id,
            name=payload.name,
            email=payload.email,
            role=UserRole.mess_admin,
            is_active=True
        )

        db.add(user)
        db.flush()

    # check if already assigned to this mess
    # here i am assuming that one mess admin can belong to many mess but letting one clg admin can
    # manage all messes
    existing_relation = (
        db.query(MessAdmin)
        .filter(
            MessAdmin.user_id == user.id,
            MessAdmin.mess_id == mess_id
        )
        .first()
    )

    if existing_relation:
        raise HTTPException(
            status_code=400,
            detail="User already assigned to this mess"
        )

    mess_admin = MessAdmin(
        user_id=UUID(str(user.id)),
        mess_id=mess_id,
        college_id=current_user.college_id
    )

    db.add(mess_admin)
    db.commit()

    return user
