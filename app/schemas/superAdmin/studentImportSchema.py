from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import uuid



class ImportValidationError(BaseModel):
    row_number: int
    message: str


class PreviewImportResponse(BaseModel):
    status: bool
    import_token: Optional[uuid.UUID] = None
    new_rows: Optional[int] = None
    update_rows: Optional[int] = None
    conflicts : List[ImportValidationError] = Field(default_factory=list)
    # expires_at: Optional[datetime] = None
    expires_at:str|None
    errors: List[ImportValidationError] = Field(default_factory=list)

class ConfirmImportResponse(BaseModel):
    status:bool
