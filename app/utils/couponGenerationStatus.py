from sqlalchemy import Enum


class GenerationStatus(str, Enum):
    pending = "pending"
    generated = "generated"
    skipped = "skipped"
    failed = "failed"