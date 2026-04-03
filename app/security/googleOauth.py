
from app.core.config import get_settings

from fastapi import Depends, HTTPException,status

from google.oauth2 import id_token
from google.auth.transport import requests


settings = get_settings()

GOOGLE_CLIENT_ID=settings.google_client_id

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')

def verify_google_token(token: str):

    try:
        payload = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        return payload

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )