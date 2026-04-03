from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.db.session import get_db
from app.security.googleOauth import verify_google_token
from app.security.jwt import createAccessToken
from uuid import UUID
import asyncio
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.mess.messAdmin import MessAdmin
from app.models.college.collegeAdmin import CollegeAdmin
from app.models.user.userSession import UserSession
from app.schemas.user.loginSchema import GoogleLoginRequest, UserLoginResponse, UserInfo
from app.utils.userRole import UserRole
from app.models.college.collegeModel import College

router = APIRouter(tags=["Google Login"])


ROLE_MODEL_MAP = {
    UserRole.student: Student,
    UserRole.mess_admin: MessAdmin,
    UserRole.college_admin: CollegeAdmin
}


@router.post("/login/google", response_model=UserLoginResponse)
async def login_with_google(
    data: GoogleLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    print(data.college_id)
    print(data.role)

    # run sync blocking google token verification in threadpool
    payload = await asyncio.to_thread(verify_google_token, data.id_token)
    # print("after verify google token")
    if not payload:
        raise HTTPException(401, "Invalid Google token")

    email = payload.get("email")
    email_verified = payload.get("email_verified")
    google_sub = payload.get("sub")
    name = payload.get("name")
    picture = payload.get("picture")

    if not email or not email_verified:
        raise HTTPException(400, "Email not verified")

    email = email.lower()
    # print(email)

    result = await db.execute(
        select(College).filter(College.id == data.college_id)
    )
    college = result.scalar_one_or_none()

    if not college:
        raise HTTPException(404, "College not found")

    college_domain = str(college.domain)
    allowed_domain = college_domain.lower()
    print(allowed_domain)

    # if not email.endswith(allowed_domain):
    #    raise HTTPException(
    #             status_code=403,
    #             detail="Institute email required"
    #          )

    # validate role
    try:
        role = UserRole(data.role)
    except ValueError:
        raise HTTPException(400, "Invalid role")

    result = await db.execute(
        select(User).filter(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(403, "User not authorized")

    if user.role != role:
        raise HTTPException(403, "Role mismatch")

    if str(user.college_id) != str(data.college_id):
        raise HTTPException(403, "College mismatch")

    model = ROLE_MODEL_MAP.get(role)

    if not model:
        raise HTTPException(403, "Unsupported role")

    # profile = db.query(model).filter(model.id == user.id).first()
    # print("profile")
    #
    # if not profile:
    #     raise HTTPException(403, "Profile not found")

    if not user.is_active:
        raise HTTPException(403, "Account inactive")

    # bind google account first login
    if user.google_sub is None:
        user.google_sub = google_sub
    elif user.google_sub != google_sub:
        raise HTTPException(401, "Google account mismatch")

    user.name = name
    user.picture = picture
    print(user.name)

    # db.add(profile)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    await db.execute(
        delete(UserSession).where(UserSession.user_id == user.id)
    )

    session = UserSession(user_id=user.id)

    db.add(session)
    await db.commit()
    await db.refresh(session)

    token_payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "college_id": str(user.college_id),
        "session_id": str(session.id)
    }
    print("generating access token")
    access_token, expires_at = createAccessToken.create_access_token(token_payload)
    print(access_token)
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserInfo(
            id=UUID(str(user.id)),
            email=str(user.email),
            name=str(user.name),
            picture=str(user.picture)
        )
    )