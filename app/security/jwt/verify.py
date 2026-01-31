from jose import JWTError,jwt
from datetime import datetime,timedelta
from app.core.config import get_settings
from app.schemas import authSchema
from fastapi.security import OAuth2PasswordBearer
from fastapi import Response,status,HTTPException,Depends


settings = get_settings()

ACCESS_TOKEN_SECRET = settings.access_token_secret
REFRESH_TOKEN_SECRET = settings.refresh_token_secret
ALGORITHM = settings.algorithm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/google")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not your validate credentials", 
                                          headers = {"WWW- Authenticate": "Bearer"})
    

    
    return verify_access_token(token,credentials_exception)

def verify_access_token(token: str, credentials_exception) -> dict:
    try:
        payload = jwt.decode(
            token,
            ACCESS_TOKEN_SECRET,
            algorithms=[ALGORITHM]
        )

        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        print(e)
        raise credentials_exception

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return payload




def verify_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            REFRESH_TOKEN_SECRET,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return payload
