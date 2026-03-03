import uuid
from fastapi import Form
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from typing import Literal
from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.student.studentImportSession import StudentImportSession
from app.services.students_csv_import import parse_and_preview_csv
from app.schemas.superAdmin.studentImportSchema import ImportValidationError,ConfirmImportResponse,PreviewImportResponse
# from app.models.superAdmin.superAdminModel import SuperAdmin
from app.core.config import get_settings
# from app.security.dependencies import get_current_super_admin
from app.schemas.student.requestResponse import StudentResponse

settings = get_settings()
MAX_CSV_FILE_SIZE = settings.max_csv_file_size
CSV_UPLOAD_TIMELIMIT= settings.csv_upload_timelimit
router = APIRouter(
    prefix="/admin/students/import",
    tags=["Student Import"])

@router.post("/preview",
            response_model=PreviewImportResponse
             )
def preview_csv(
    mode: Literal["insert", "update"] = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),

    # current_admin = Depends(get_current_super_admin)
):

    print(mode)

    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
           status_code=400,
           detail="Only .csv files are allowed."
    )

    content = file.file.read()
    if len(content) > MAX_CSV_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Maximum allowed size is 2MB."
        )

    if mode not in {"insert", "update"}:
        raise HTTPException(400, "mode must be insert or update")

    csv_content = content.decode("utf-8")

    existing_emails = {
        email for (email,) in db.query(Student.email).all()
    }

    preview = parse_and_preview_csv(csv_content, existing_emails, mode)

    # no errors or conflicts allowed
    if not preview["status"]:
        return PreviewImportResponse(
            status=False,
            errors=[
                ImportValidationError(
                    row_number=err["row_number"],
                    message=err["message"]
                )
                for err in preview["errors"]
            ],
            conflicts=[
                ImportValidationError(
                    row_number=conf["row_number"],
                    message=conf["message"]
                )
                for conf in preview["conflicts"]
            ],
            new_rows=0,
            update_rows=0,
            import_token=None,
            expires_at=None
        )
    # expires_at = datetime.utcnow() + timedelta(minutes=CSV_UPLOAD_TIMELIMIT)


    expires_at = datetime.now(timezone.utc) + timedelta(minutes=CSV_UPLOAD_TIMELIMIT)

    session = StudentImportSession(
        # admin_id=current_admin.id,
        to_insert=preview["to_insert"],
        to_update=preview["to_update"],
        expires_at=expires_at
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    expire_time_ist = session.expires_at.astimezone(
        ZoneInfo("Asia/Kolkata")
    )

    expire_time = expire_time_ist.strftime("%H:%M:%S")

    return PreviewImportResponse(
        status=True,
        import_token=session.id,
        new_rows=len(preview["to_insert"]),
        update_rows=len(preview["to_update"]),
        conflicts=[],
        expires_at=expire_time,
        errors=[]
    )

from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

@router.post(
    "/confirm",
    response_model=ConfirmImportResponse
)
def confirm_import(
    import_token: uuid.UUID,
    db: Session = Depends(get_db),
):

    session = db.query(StudentImportSession).filter(
        StudentImportSession.id == import_token
    ).first()

    # Token not found
    if not session:
        return ConfirmImportResponse(status=False)

    # Token expired → delete row
    if session.expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return ConfirmImportResponse(status=False)

    try:
        to_insert = session.to_insert or []
        to_update = session.to_update or []

        # One-time use → delete staging row
        db.delete(session)

        # Insert
        if to_insert:
            db.add_all(Student(**row) for row in to_insert)

        # Update
        if to_update:
            emails = [row["email"] for row in to_update]

            existing_students = db.query(Student).filter(
                Student.email.in_(emails)
            ).all()

            existing_map = {s.email: s for s in existing_students}

            for row in to_update:
                student = existing_map.get(row["email"])
                if student:
                    student.name = row["name"]
                    student.roll_number = row["roll_number"]
                    student.branch = row["branch"]
                    student.batch = row["batch"]
                    student.is_active = row["is_active"]

        db.commit()
        return ConfirmImportResponse(status=True)

    except (IntegrityError, SQLAlchemyError):
        db.rollback()
        return ConfirmImportResponse(status=False)