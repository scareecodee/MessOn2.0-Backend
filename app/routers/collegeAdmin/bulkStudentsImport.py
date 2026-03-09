from uuid import UUID
import uuid
from fastapi import Form
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException,status
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from typing import Literal
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.db.session import get_db
from app.models.student.studentImportSession import StudentImportSession
from app.services.students_csv_import import parse_and_preview_csv
from app.schemas.collegeAdmin.studentImportSchema import ImportValidationError,ConfirmImportResponse,PreviewImportResponse
from app.security.dependencies.getCurrentRole import get_current_role
from app.models.user.userModel import User
from app.models.student.studentModel import Student
from app.models.mess.messModel import Mess
from app.utils.userRole import UserRole
from app.core.config import get_settings


settings = get_settings()
MAX_CSV_FILE_SIZE = settings.max_csv_file_size
CSV_UPLOAD_TIMELIMIT= settings.csv_upload_timelimit


router = APIRouter(
    prefix="/admin/import/students",
    tags=["Student Import"])

@router.post(
             "/preview/{mess_id}",
            response_model=PreviewImportResponse
             )
def preview_csv(
    mess_id:UUID,
    mode: Literal["insert", "update"] = Form(...),
    file: UploadFile = File(...),
    current_admin:User=Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db)

):
    mess = db.query(Mess).filter(
        Mess.id == mess_id,
        Mess.college_id == current_admin.college_id
    ).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot access this mess."
        )


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
        email for (email,) in db.query(User.email).all()
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



@router.post(
    "/confirm/{mess_id}",
    response_model=ConfirmImportResponse
)
def confirm_import(
    mess_id: UUID,
    import_token: uuid.UUID,
    current_admin:User=Depends(get_current_role(UserRole.college_admin)),
    db: Session = Depends(get_db),
):

    session = db.query(StudentImportSession).filter(
        StudentImportSession.id == import_token
    ).first()

    # Token not found
    # print("Inside cnf")
    if not session:
        return ConfirmImportResponse(status=False)

    # Token expired → delete row

    if session.expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return ConfirmImportResponse(status=False)
    print("token verified")

    try:
        to_insert = session.to_insert or []
        to_update = session.to_update or []
        # print("to inerrt",to_insert)
        # One-time use → delete staging row
        db.delete(session)

        emails = [row["email"] for row in to_insert]

        existing_students = (
            db.query(Student)
            .join(User)
            .filter(User.email.in_(emails))
            .all()
        )

        # print("inserting raw ")

        if existing_students:
            raise HTTPException(
                status_code=400,
                detail="Some students already belong to another mess."
            )

        # Insert
        print("before to_insert")
        if to_insert:
            for row in to_insert:
                user = User(
                    email=str(row["email"]),
                    name=str(row["name"]),
                    role=UserRole.student,
                    college_id=current_admin.college_id,
                    is_active=bool(row["is_active"])
                )

                db.add(user)
                db.flush()  # get user.id

                student = Student(
                    user_id=user.id,
                    college_id=current_admin.college_id,
                    mess_id=mess_id,
                    roll_number=str(row["roll_number"]),
                    branch=str(row["branch"]),
                    batch=int(str(row["batch"])),
                )


                db.add(student)
        print("before insert add")

        if to_update:

            emails = [row["email"] for row in to_update]

            existing_students = (
                db.query(Student)
                .join(User)
                .filter(User.email.in_(emails))
                .all()
            )

            update_map = {row["email"]: row for row in to_update}

            for student in existing_students:
                row = update_map.get(student.user.email)

                if row:
                    student.branch = row["branch"]
                    student.batch = row["batch"]
                    student.roll_number = row["roll_number"]

                    student.user.name = row["name"]
                    student.user.is_active = row["is_active"]
        print("one step away from commit")
        db.commit()
        return ConfirmImportResponse(status=True)

    # except (IntegrityError, SQLAlchemyError):
    #     db.rollback()
    #     return ConfirmImportResponse(status=False)

    except Exception as e:
        db.rollback()
        print("IMPORT ERROR:", repr(e))
        raise