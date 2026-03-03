from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.security.googleOauth import verify_google_token

from app.db.session import get_db
from app.schemas.student.authSchema import (
    GoogleLoginRequest,
    LoginResponse,
    UserResponse
)
from app.models.student.studentModel import Student
from app.security.jwt import access

router = APIRouter(
    tags = ['Student Login']
)

ALLOWED_DOMAIN = "@iiit-bh.ac.in"


@router.post(
    "/login/google",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK
)
def login_with_google(
    data: GoogleLoginRequest,
    db: Session = Depends(get_db)
    
):
    # payload = googleOauth.verify_google_token(data.id_token)
    

    # print(data)
    payload = verify_google_token(data.id_token)
    # print(payload)


    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    provider = payload.get("firebase", {}).get("sign_in_provider")

    # if provider != "google.com":
    #     raise HTTPException(401, "Only Google login allowed")


    email = payload.get("email")
    email_verified = payload.get("email_verified")
    google_sub = payload.get("sub")
    name = payload.get("name")
    picture = payload.get("picture")

    if not email or not email_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    email = email.lower()

    if not email.endswith("@iiit-bh.ac.in"):
        raise HTTPException(
            status_code=403,
            detail="Institute email required"
        )

    student = (
        db.query(Student)
        .filter(Student.email == email)
        .first()
    )

    
    if not student:
        raise HTTPException(
            status_code=403,
            detail="Student not authorized by admin"
        )

    if not student.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

    # First login → bind Google account
    if student.google_sub is None:
        student.google_sub = google_sub

    # Subsequent logins → enforce binding
    elif student.google_sub != google_sub:
        raise HTTPException(
            status_code=401,
            detail="Google account mismatch"
        )

    # Update profile 
    # print(name)
    # print(picture)
    # print(google_sub)
    student.name = name
    student.picture = picture

    db.add(student)
    db.commit()
    db.refresh(student)

    access_token, expires_at = access.create_access_token(
        {"sub": str(student.id)}
    )
    print(access_token)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserResponse(
            id=student.id,
            email=student.email,
            name=student.name,
            picture=student.picture
        )
    )
