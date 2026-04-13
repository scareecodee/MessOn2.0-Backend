from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.security.jwt.getTokenPayload import get_token_payload
from app.models.rootAdmin.rootAdminUserModel import RootAdmin
from app.security.verifySession.session import verify_session
from app.utils.userRole import UserRole
from app.models.user.userModel import User


async def get_current_root_admin(
    payload: dict = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db)
):
    if payload.get("role") != UserRole.root_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )

    user_id = payload.get("sub")
    # session_id = payload.get("session_id")

    # session = await verify_session(session_id, db)
    #
    # if str(session.user_id) != str(user_id):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Session-user mismatch"
    #     )

    users = await db.execute(
        select(User).filter(User.id== user_id)
    )
    user = users.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root admin not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Root admin inactive"
        )

    return user