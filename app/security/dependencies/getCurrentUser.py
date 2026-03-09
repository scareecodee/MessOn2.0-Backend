from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.models.user.userModel import User
from app.security.jwt.getTokenPayload import get_token_payload
from app.db.session import get_db


def get_current_user(
    payload: dict = Depends(get_token_payload),
    db: Session = Depends(get_db)
):

    user_id = payload["sub"]
    college_id = payload["college_id"]

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive"
        )

    if str(user.college_id) != college_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid college access"
        )

    return user