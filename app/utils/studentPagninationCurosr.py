from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException
from app.core.config import get_settings



settings = get_settings()

CURSOR_SECRET_KEY = settings.cursor_secret

serializer = URLSafeSerializer(CURSOR_SECRET_KEY)

def encode_student_cursor(roll_number: str, created_at: datetime, student_id: UUID) -> str:
    payload = {
        "roll_number": roll_number,
        "created_at": created_at.isoformat(),
        "id": str(student_id)
    }

    return serializer.dumps(payload)


def decode_student_cursor(cursor: str):
    try:
        data = serializer.loads(cursor)
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid cursor")

    try:
        roll_number = data["roll_number"]
        created_at = datetime.fromisoformat(data["created_at"])
        student_id = UUID(data["id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Malformed cursor")

    return roll_number, created_at, student_id