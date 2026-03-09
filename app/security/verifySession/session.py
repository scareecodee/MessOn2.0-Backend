from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user.userSession import UserSession


def verify_session(session_id: str, db: Session) -> type[UserSession]:

    session = db.query(UserSession).filter(
        UserSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )

    if not session.status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )

    return session