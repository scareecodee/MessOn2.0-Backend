from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.college.collegeModel import College
from typing import List
from app.schemas.collegeAdmin.collegeDetails import CollegeDetails

router = APIRouter(tags=["College"])

@router.get("/fetch-colleges", response_model=List[CollegeDetails])
def fetch_colleges(db: Session = Depends(get_db)):

    colleges = (
        db.query(College)
        .filter(College.status == True)
        .all()
    )

    if not colleges:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No colleges found"
        )

    return [
        CollegeDetails(
            college_id=str(c.id),
            college_name=str(c.name)
        )
        for c in colleges
    ]