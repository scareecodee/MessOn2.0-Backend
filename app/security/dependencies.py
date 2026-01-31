from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from app.security.jwt.verify import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/login")

def get_current_user(token:str=Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers = {"WWW- Authenticate": "Bearer"}
        )

    return user_id