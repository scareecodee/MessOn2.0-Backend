from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.security.googleOauth import verify_google_token
from app.db.session import get_db
from app.schemas.student.authSchema import (
    GoogleLoginRequest,
    LoginResponse,
    UserResponse
)
from app.models.mess.messAdminModel import MessAdmin
from app.security.jwt import access

router = APIRouter(
    tags = ['Mess Admin Login']
)

# ALLOWED_DOMAIN = "@iiit-bh.ac.in"


@router.post(
    "/mess-admin/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK
)
def login_with_google(
    data: GoogleLoginRequest,
    db: Session = Depends(get_db)
    
):

    payload = verify_google_token(data.id_token)
    # print("printing mess_Admin payload ", payload)


    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    provider = payload.get("firebase", {}).get("sign_in_provider")

    


    email = payload.get("email")
    email_verified = payload.get("email_verified")
    google_sub = payload.get("sub")
    name = payload.get("name")
    picture = payload.get("picture")

    if not email or not email_verified:
        raise HTTPException(status_code=400, detail="Email not verified")

    email = email.lower()

    messAdmin = (
        db.query(MessAdmin)
        .filter(MessAdmin.email == email)
        .first()
    )

    
    if not messAdmin:
        raise HTTPException(
            status_code=403,
            detail="Mess_Admin not authorized by admin"
        )

    if not messAdmin.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

   
    if messAdmin.google_sub is None:
        messAdmin.google_sub = google_sub

   
    elif messAdmin.google_sub != google_sub:
        raise HTTPException(
            status_code=401,
            detail="Google account mismatch"
        )

    messAdmin.name = name
    messAdmin.picture=picture
   

    db.add(messAdmin)
    db.commit()
    db.refresh(messAdmin)

    access_token, expires_at = access.create_access_token(
        {"sub": str(messAdmin.id)}
    )
    print("Mess Admin access Token ")
    print(access_token)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=UserResponse(
            id=messAdmin.id,
            email=messAdmin.email,
            name=messAdmin.name,
            picture=messAdmin.picture
        )
    )
