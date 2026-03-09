from jose import JWTError,jwt
from datetime import datetime,timedelta,timezone
from app.core.config import get_settings


settings = get_settings()

SECRET_KEY = settings.access_token_secret
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_DAYS= settings.access_token_expire_days

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'login')


def create_access_token(payload: dict) -> tuple[str, datetime]:

    to_encode = payload.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=ACCESS_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt, expire