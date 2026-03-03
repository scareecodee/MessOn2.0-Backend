from jose import JWTError,jwt
from app.core.config import get_settings
from fastapi import status,HTTPException

settings = get_settings()

ACCESS_TOKEN_SECRET = settings.access_token_secret
# REFRESH_TOKEN_SECRET = settings.refresh_token_secret
ALGORITHM = settings.algorithm

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/google")

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                           detail=f"Could not your validate credentials", 
#                                           headers = {"WWW- Authenticate": "Bearer"})
    

    
    # return verify_access_token(token,credentials_exception)

def verify_access_token(token: str): #-> dict:
    # print(token)
    try:
        payload = jwt.decode(
            token,
            ACCESS_TOKEN_SECRET,
            algorithms=[ALGORITHM]
        )
        # print(payload)

        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate your credentials"
            )

    except JWTError as e:
        # print(e)
        raise HTTPException(
                status_code=401,
                detail="Could not validate your credentials"
            )
    

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return payload




# def verify_refresh_token(token: str) -> dict:
#     try:
#         payload = jwt.decode(
#             token,
#             REFRESH_TOKEN_SECRET,
#             algorithms=[ALGORITHM]
#         )
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired refresh token"
#         )

#     if payload.get("type") != "refresh":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token type"
#         )

#     return payload
