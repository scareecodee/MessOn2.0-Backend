from enum import Enum

class ComplaintStatusEnum(str, Enum):
    pending = "pending"
    progress = "progress"
    resolved = "resolved"
