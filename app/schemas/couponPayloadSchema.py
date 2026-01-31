from pydantic import BaseModel
from datetime import date


class CouponPayload(BaseModel):
    v: int                 
    cid: str               
    uid: str               
    d: date                
    m: str                 
    iat: int               
    exp: int               
    sig: str               
