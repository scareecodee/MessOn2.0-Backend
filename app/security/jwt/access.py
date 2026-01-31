from jose import JWTError,jwt
from datetime import datetime,timedelta
from app.core.config import get_settings
# from app.schemas import authSchema
# from fastapi.security import OAuth2PasswordBearer
# from fastapi import Depends

settings = get_settings()

SECRET_KEY = settings.access_token_secret
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_DAYS= settings.access_token_expire_days

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')


def create_access_token(data:dict) -> tuple[str, datetime]:
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(days= ACCESS_TOKEN_EXPIRE_DAYS)
    type="access"
    to_encode.update({"exp": expire, "type":"access"})

    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,ALGORITHM)
    

    return encoded_jwt, expire