from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime
from uuid import UUID
from fastapi import HTTPException
from app.core.config import get_settings

settings = get_settings()

CURSOR_SECRET_KEY = settings.cursor_secret
serializer = URLSafeSerializer(CURSOR_SECRET_KEY)

def encode_complaint_cursor(
    created_at: datetime,
    likes_count: int,
    complaint_id: UUID
) -> str:

    payload = {
        "created_at": created_at.isoformat(),
        "likes_count": likes_count,
        "id": str(complaint_id)
    }

    return serializer.dumps(payload)


def decode_complaint_cursor(cursor: str):

    try:
        data = serializer.loads(cursor)

    except BadSignature:
        raise HTTPException(
            status_code=400,
            detail="Invalid cursor"
        )

    try:

        return (
            datetime.fromisoformat(
                data["created_at"]
            ),
            data["likes_count"],
            UUID(data["id"])
        )

    except (KeyError, ValueError):

        raise HTTPException(
            status_code=400,
            detail="Malformed cursor"
        )