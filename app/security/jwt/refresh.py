# from datetime import datetime,timedelta
# from app.config import get_settings
# import uuid
# from jose import JWTError,jwt


# settings = get_settings()

# REFRESH_TOKEN_SECRET = settings.refresh_token_key
# ALGORITHM = settings.algorithm
# REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days

# def create_refresh_token(data:dict):
#     payload=data.copy()
#     payload = {
#         "user_id":data,
#         "type" : "refresh",
#         "exp" : datetime.utcnow() + timedelta(days= REFRESH_TOKEN_EXPIRE_DAYS)
#         "jti": str(uuid.uuid4())
#         "iat": datetime.utcnow()
#     }

#     return jwt.encode(
#         payload,
#         REFRESH_TOKEN_SECRET,
#         ALGORITHM
#     )
