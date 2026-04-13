from jose import JWTError,jwt
from app.core.config import get_settings
from fastapi import status,HTTPException

settings = get_settings()

ACCESS_TOKEN_SECRET = settings.access_token_secret
ALGORITHM = settings.algorithm

from jose import jwt, JWTError
from fastapi import HTTPException, status


def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            ACCESS_TOKEN_SECRET,
            algorithms=[ALGORITHM]
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return payload
