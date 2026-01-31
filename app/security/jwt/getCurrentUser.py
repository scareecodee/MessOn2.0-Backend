# from jose import JWTError,jwt
# from datetime import datetime,timedelta
# from app.core.config import get_settings
# from app.schemas import auth
# from fastapi.security import OAuth2PasswordBearer
# from fastapi import Depends

# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                                           detail=f"Could not your validate credentials", 
#                                           headers = {"WWW- Authenticate": "Bearer"})
    

    
#     return verify_access_token(token,credentials_exception)