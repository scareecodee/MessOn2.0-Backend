from fastapi import APIRouter, Depends, HTTPException, status,Response
from sqlalchemy.orm import Session
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from uuid import UUID
# from app.models.mess.messModel import Mess
from app.models.mess.messAdmin import MessAdmin
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete/mess",
    tags=["Manage Mess"]
)
@router.delete("/{mess-admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mess_admin(
    mess_admin_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_role(UserRole.college_admin))
):

    mess_admin = db.query(MessAdmin).filter(
        MessAdmin.user_id == mess_admin_id,
        MessAdmin.college_id == current_user.college_id
    ).first()

    if not mess_admin:
        raise HTTPException(404, "Mess not found")

    db.delete(mess_admin)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )