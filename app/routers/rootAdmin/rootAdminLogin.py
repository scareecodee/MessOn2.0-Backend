from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.rootAdmin.rootAdminUserModel import RootAdmin
from app.utils.hash_pwd import verify_password
from app.security.jwt.createAccessToken import create_access_token
from app.services.createUserSession import create_user_session
from app.schemas.rootAdmin.rootAdminLogin import RootAdminLoginRequest
from app.models.user.userModel import User

router = APIRouter(tags=["Root Admin Login"])


@router.post("/root-admin/login")
async def root_login(
    payload: RootAdminLoginRequest,
    db: AsyncSession = Depends(get_db)
):

    users = await db.execute(
        select(User).where(User.email == payload.email)
    )
    user = users.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    admins = await db.execute(
        select(RootAdmin).where(RootAdmin.user_id == user.id)
    )
    admin = admins.scalar_one_or_none()

    if not verify_password(payload.password, admin.password):
         raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive account")

    session = await create_user_session(db, user.id)
    # session = None
    token_payload = {
        "sub": str(user.id),
        "role": "root_admin",
        "college_id": None,
        "session_id": str(session.id)
    }

    access_token, expires_at = create_access_token(token_payload)

    return {
        "access_token": access_token,
        "expires_at": expires_at,
        "token_type": "bearer"
    }