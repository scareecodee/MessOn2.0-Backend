from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy import select, tuple_, or_, cast, String
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.student.studentModel import Student
from app.models.user.userModel import User
from app.models.mess.messModel import Mess
from app.security.dependencies.getCurrentRole import get_current_role
from app.utils.userRole import UserRole
from app.schemas.student.fetchStudentsSchema import StudentListResponse
from app.schemas.student.studentFilter import StudentFilterParams
from app.utils.cursorEncodeDecode import encode_cursor, decode_cursor

router = APIRouter(
    prefix="/admin",
    tags=["Fetch Students"]
)

@router.get("/fetch-students/{mess_id}", response_model=StudentListResponse)
def get_students(
    mess_id:UUID,
    current_admin:User=Depends(get_current_role(UserRole.college_admin)),
    params: StudentFilterParams = Depends(),
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

    query = (
        select(Student)
        .join(User, User.id == Student.user_id)
        .where(
            Student.mess_id == mess_id,
            Student.college_id == current_admin.college_id
        )
    )

    # # ---------------- BATCH CHIP FILTER ----------------
    # if params.batch:
    #     query = query.where(Student.batch == params.batch)

    # ---------------- UNIFIED SEARCH ----------------
    if params.search:
        search_lower = params.search.lower()

        query = query.where(
            or_(
                User.name.ilike(f"%{search_lower}%"),
                Student.roll_number.ilike(f"{search_lower}%"),
                User.email.ilike(f"{search_lower}%"),
                Student.branch.ilike(f"{search_lower}%"),
                cast(Student.batch, String).ilike(f"{search_lower}%")
            )
        )

    # ----------G------ ORDER ----------------
    query = query.order_by(
        Student.roll_number.asc(),
        User.created_at.desc(),
        # Student.user_id.desc
        User.id.desc()
    )

    if params.cursor:
        cursor_roll, cursor_created_at, cursor_id = decode_cursor(params.cursor)

        query = query.where(
            tuple_(Student.roll_number, User.created_at, User.id)
            > (cursor_roll, cursor_created_at, cursor_id)
        )

    query = query.limit(params.limit + 1)

    result = db.execute(query).scalars().all()

    has_more = len(result) > params.limit
    students = result[:params.limit]

    next_cursor = None

    if has_more:
        last_student = students[-1]
        next_cursor = encode_cursor(
            last_student.roll_number,
            last_student.user.created_at,
            last_student.user.id
        )

    return {
        "students_list": [
            {
                "student_uuid":s.user.id,
                "name": s.user.name,
                "roll_number": s.roll_number,
                "email": s.user.email,
                "branch": s.branch,
                "batch": s.batch,
                "is_active": s.user.is_active,
                "picture": s.user.picture,
            }

            for s in students

        ],
        "next_cursor": next_cursor
    }