from pydantic import BaseModel, Field
from typing import Optional
from datetime import date,datetime


class CouponPayload(BaseModel):
    couponId: str
    userId: str
    date: date
    mealSlot:str
    mealType:str
    expiresAt: int = Field(..., description="UTC epoch seconds")
    usedAt: Optional[int] = Field(None, description="UTC epoch seconds")
    signature: str

class QrResponseSchema(BaseModel):
    valid:bool

class QrExpired(BaseModel):
    expired:bool
    
class QrUsed(BaseModel):
    markedAsTrue:bool=False
    



