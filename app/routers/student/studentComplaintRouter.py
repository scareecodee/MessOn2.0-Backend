from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.student.studentComplaintModel import Feedback
from app.schemas.student.studentComplaintSchema import CreateComplaint,ComplaintResponse,ComplaintRegistered
from app.security.dependencies import get_current_user
from app.models.student.studentModel import Student
from sqlalchemy import select
from datetime import datetime
from app.core.config import get_settings

router = APIRouter(
    prefix="",
    tags=["Student Complaint"]
)

settings=get_settings()

@router.post("/create/complaint",response_model=ComplaintRegistered)
def create_complaint(
    payload: CreateComplaint,
    db: Session = Depends(get_db),
    current_student = Depends(get_current_user),
):
    
    complaint =Feedback(

    )
    db.add(complaint)
    db.flush()


    
    subquery = (
    select(Complaint.student_id)
    .order_by(Complaint.created_at.desc())
    .offset(settings.max_notifications)
)

    db.query(Complaint).filter(
        Complaint.student_id.in_(subquery)
    ).delete(synchronize_session=False)

    db.commit()

    return ComplaintRegistered(
        registered=True
    )

# @router.get("/fetch/complaint")
@router.get("/fetch/complaint", response_model=list[ComplaintResponse])
def fetch_new_complaints(
    db: Session = Depends(get_db)
):
    
    complaint = db.query(Complaint)

    if  not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "No Complaints Found"
        )

    complaints = (
        complaint
        .order_by(Complaint.created_at.asc())  # oldest → newest
        .all()
    )

    return complaints


@router.post("/complaints/mark-all-as-read")
def mark_seen(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_user),
):
    # print(type(Student.notifications_seen_at))
    print("All messeges read")
    current_student.notifications_seen_at = datetime.utcnow()
    db.commit()

    return {"message": "Seen"}
