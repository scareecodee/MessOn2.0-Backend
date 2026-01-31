import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.studentModel import Student
from app.services.students_csv_import import parse_and_preview_csv

router = APIRouter(prefix="/admin/students/import", tags=["Admin Import"])

# TEMP cache – replace with Redis later
IMPORT_CACHE = {}



@router.post("/preview")
def preview_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files allowed")

    csv_content = file.file.read().decode("utf-8")

    existing_emails = {
        s.email for s in db.query(Student.email).all()
    }

    try:
        preview = parse_and_preview_csv(csv_content, existing_emails)
    except ValueError as e:
        raise HTTPException(400, str(e))

    import_token = str(uuid.uuid4())

    IMPORT_CACHE[import_token] = {
        "csv": csv_content,
        "preview": preview
    }

    return {
        "import_token": import_token,
        "total_rows": preview["total"],
        "to_insert": len(preview["to_insert"]),
        "to_update": len(preview["to_update"]),
        "errors": preview["errors"]
    }



@router.post("/confirm")
def confirm_import(
    import_token: str,
    db: Session = Depends(get_db)
):
    cached = IMPORT_CACHE.get(import_token)
    if not cached:
        raise HTTPException(400, "Invalid or expired import token")

    preview = cached["preview"]

    try:
        # inserts
        for data in preview["to_insert"]:
            db.add(Student(**data))

        # updates
        for data in preview["to_update"]:
            student = (
                db.query(Student)
                .filter(Student.email == data["email"])
                .first()
            )

            if student:
                student.name = data["name"]
                student.is_active = data["is_active"]

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(500, str(e))

    del IMPORT_CACHE[import_token]

    return {
        "status": "Import successful",
        "inserted": len(preview["to_insert"]),
        "updated": len(preview["to_update"])
    }

