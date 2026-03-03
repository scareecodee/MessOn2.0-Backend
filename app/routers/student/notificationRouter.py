from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.mess.notificationModel import Notification
from app.schemas.student.notificationSchema import NotificationCreate,NotificationResponse
from app.security.dependencies import get_current_user
from app.models.student.studentModel import Student
from sqlalchemy import select
from datetime import datetime
from app.core.config import get_settings

router = APIRouter(
    prefix="",
    tags=["Notification"]
)

settings=get_settings()

@router.post("/create/notifications")
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    # admin = Depends(get_current_admin),
):
    
    notification = Notification(
        subject=payload.subject,
        description=payload.description,
    )
    db.add(notification)
    db.flush()  

    
    subquery = (
    select(Notification.id)
    .order_by(Notification.created_at.desc())
    .offset(settings.max_notifications)
)

    db.query(Notification).filter(
        Notification.id.in_(subquery)
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Notification created successfully"}


@router.get("/notifications", response_model=list[NotificationResponse])
def get_new_notifications(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_user),
):
    query = (
        db.query(Notification)
        .filter(Notification.student_id == current_student.id)
    )

    if current_student.notifications_seen_at:
        query = query.filter(
            Notification.created_at > current_student.notifications_seen_at
        )

    notifications = (
        query
        .order_by(Notification.created_at.asc())
        .all()
    )

    return notifications



@router.post("/notifications/mark-all-as-read")
def mark_seen(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_user),
):
    # print(type(Student.notifications_seen_at))
    print("All messeges read")
    current_student.notifications_seen_at = datetime.utcnow()
    db.commit()

    return {"message": "Seen"}

