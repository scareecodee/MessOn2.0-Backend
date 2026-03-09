# from jose import JWTError,jwt
# from datetime import datetime,timedelta
from app.core.config import get_settings
# from app.schemas import user
# from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from google.oauth2 import id_token
from google.auth.transport import requests


settings = get_settings()

GOOGLE_CLIENT_ID=settings.google_client_id

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')

def verify_google_token(token: str):

    # print("inside verify_google_token")
    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        # print("returning payload")
        return payload

    except Exception as e:
       print("Google token verification failed:", str(e))
       return None

    return None
