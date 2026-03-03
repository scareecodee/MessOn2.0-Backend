from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from typing import List
from collections import Counter

from app.db.session import get_db
from app.schemas.student.requestResponse import (
    StudentCreate,
    AddStudentManuallyResponse,
    AddManuallyConflictResponse
)
from app.models.student.studentModel import Student


router = APIRouter(
    prefix="/admin/students/import",
    tags=["Student Import"]
)


@router.post(
    "/manually",
    response_model=AddStudentManuallyResponse
)
def add_students_manually(
    response: Response,
    students: List[StudentCreate],
    db: Session = Depends(get_db),
):
    conflicts = []

    # ---------------- IN-REQUEST DUPLICATE CHECK ----------------
    email_counts = Counter([s.email for s in students])
    roll_counts = Counter([s.roll_number for s in students])

    for s in students:
        if email_counts[s.email] > 1 and roll_counts[s.roll_number] > 1:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Duplicate email and roll number found in request"
                )
            )
        elif email_counts[s.email] > 1:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Duplicate email in request"
                )
            )
        elif roll_counts[s.roll_number] > 1:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Duplicate roll number in request"
                )
            )

    # ---------------- DATABASE EXISTENCE CHECK ----------------
    emails = [s.email for s in students]
    roll_numbers = [s.roll_number for s in students]

    existing_students = db.query(Student).filter(
        or_(
            Student.email.in_(emails),
            Student.roll_number.in_(roll_numbers)
        )
    ).all()

    existing_email_set = {student.email for student in existing_students}
    existing_roll_set = {student.roll_number for student in existing_students}

    for s in students:
        if s.email in existing_email_set and s.roll_number in existing_roll_set:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Email and roll number already exist in database"
                )
            )
        elif s.email in existing_email_set:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Email already exists in database"
                )
            )
        elif s.roll_number in existing_roll_set:
            conflicts.append(
                AddManuallyConflictResponse(
                    email=s.email,
                    roll_number=s.roll_number,
                    message="Roll number already exists in database"
                )
            )

    # Remove duplicate conflict objects
    unique_conflicts = {
        (c.email, c.roll_number, c.message): c
        for c in conflicts
    }.values()

    if unique_conflicts:
        response.status_code = status.HTTP_409_CONFLICT
        print("in response")
        return AddStudentManuallyResponse(
            status=False,
            conflicts=list(unique_conflicts)
        )

    # ---------------- INSERT BLOCK WITH DB SAFETY ----------------
    db_students = [
        Student(
            name=s.name,
            roll_number=s.roll_number,
            email=s.email,
            branch=s.branch,
            batch=s.batch,
            is_active=s.isActive,
            picture=s.picture
        )
        for s in students
    ]

    try:
        db.add_all(db_students)
        db.commit()
    except IntegrityError:
        db.rollback()
        response.status_code = status.HTTP_409_CONFLICT
        return AddStudentManuallyResponse(
            status=False,
            conflicts=[
                AddManuallyConflictResponse(
                    email="unknown",
                    roll_number="unknown",
                    message="Unique constraint violation occurred."
                )
            ]
        )

    response.status_code = status.HTTP_201_CREATED
    return AddStudentManuallyResponse(
        status=True,
        conflicts=[]
    )