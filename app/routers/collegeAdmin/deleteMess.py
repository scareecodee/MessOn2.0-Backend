from fastapi import APIRouter, Depends, HTTPException, status,Response
from sqlalchemy.orm import Session
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from uuid import UUID
from app.models.mess.messModel import Mess
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete",
    tags=["Mess Admin Management"]
)
@router.delete("/mess/{mess_id}")
def delete_mess(
    mess_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_role(UserRole.college_admin))
):

    mess = db.query(Mess).filter(
        Mess.id == mess_id,
        Mess.college_id == current_user.college_id
    ).first()

    if not mess:
        raise HTTPException(404, "Mess not found")

    db.delete(mess)
    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )