# from jose import JWTError,jwt
# from datetime import datetime,timedelta
from app.core.config import get_settings
# from app.schemas import auth
# from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from google.oauth2 import id_token
from google.auth.transport import requests


settings = get_settings()

GOOGLE_CLIENT_ID=settings.google_client_id

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                           detail=f"Could not your validate credentials", 
#                                           headers = {"WWW- Authenticate": "Bearer"})
    

    
    # return verify_access_token(token,credentials_exception)


def verify_google_token(token: str):
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return payload
    except Exception:
        return None
