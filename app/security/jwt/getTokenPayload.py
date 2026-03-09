from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.mess.messAdmin import MessAdmin
from app.security.jwt.verifyAccessToken import verify_access_token
from app.models.college.collegeAdmin import CollegeAdmin
from app.security.verifySession.session import verify_session

security = HTTPBearer()


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials.strip()



    try:
        payload = verify_access_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")
        college_id = payload.get("college_id")
        session_id = payload.get("session_id")

        if not all([user_id, role, college_id, session_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    verify_session(session_id, db)

    return payload