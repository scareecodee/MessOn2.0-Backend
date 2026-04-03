from enum import Enum

class BillRangeType(str, Enum):
    last_n_days = "last_n_days"
    custom = "custom"