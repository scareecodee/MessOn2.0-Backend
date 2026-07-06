from enum import Enum

class CouponGenerationStatus(str, Enum):
    pending = "pending"
    generated = "generated"
    generating = "generating"
    failed = "failed"
