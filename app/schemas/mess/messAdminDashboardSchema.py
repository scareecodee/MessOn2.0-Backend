from pydantic import BaseModel
from datetime import datetime

class TotalCouponsGenerated(BaseModel):
    total_coupon_count:int
   

class TotalScannedCoupon(BaseModel):
   breakfastCount:int
   lunchCount:int
   dinnerCount:int
