from datetime import datetime, timedelta, timezone

from app.models.user.userSession import UserSession
from app.core.config import get_settings

settings = get_settings()

from datetime import datetime, timedelta, timezone
from app.models.user.userSession import UserSession

async def create_user_session(db, user_id):

    session = UserSession(
        user_id=user_id,
        is_active=True,
        expires_at=datetime.now(timezone.utc) + timedelta(days =settings.access_token_expire_days)
    )

    db.add(session)

    await db.flush()
    await db.commit()
    await db.refresh(session)
    print("SESSION CREATED",session)

    return session