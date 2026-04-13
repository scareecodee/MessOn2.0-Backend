from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.db.session import get_db
from app.security.jwt.verifyAccessToken import verify_access_token
from app.security.verifySession.session import verify_session

security = HTTPBearer()


# async def get_token_payload(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: AsyncSession = Depends(get_db)
# ):
#     token = credentials.credentials.strip()
#
#     try:
#         payload = verify_access_token(token)
#
#         user_id = payload.get("sub")
#         role = payload.get("role")
#         college_id = payload.get("college_id")
#         session_id = payload.get("session_id")
#
#         if not all([user_id, role, college_id, session_id]):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token payload"
#             )
#
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )
#
#     await verify_session(session_id, db)
#
#     return payload

async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials.strip()

    try:
        payload = verify_access_token(token)

        user_id = payload.get("sub")
        role = payload.get("role")
        college_id = payload.get("college_id")
        session_id = payload.get("session_id")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        if role == "root_admin":
            return payload

        if not session_id or not college_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        await verify_session(session_id, db)

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )