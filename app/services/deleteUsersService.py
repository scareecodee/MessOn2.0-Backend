from fastapi import HTTPException
from sqlalchemy import delete, select

from app.models.college.collegeAdmin import CollegeAdmin
from app.models.mess.messAdmin import MessAdmin
from app.models.student.studentModel import Student
from app.utils.userRole import UserRole
from sqlalchemy import text
from fastapi import HTTPException
import asyncio

MAX_RETRIES = 3


async def delete_users(payload, db, current_user):

    if payload.role == UserRole.student:

        students = (
            delete(Student)
            .where(
                Student.user_id.in_(payload.users_id),
                Student.college_id == current_user.college_id
            )
            .returning(Student.user_id)
        )

        delete_students = await db.execute(students)
        deleted_ids = delete_students.scalars().all()

        if not deleted_ids:
            raise HTTPException(404, "Users not found")
        await db.commit()

        return deleted_ids


    elif payload.role == UserRole.mess_admin:

        mess_admins = (
            delete(MessAdmin)
            .where(
                MessAdmin.user_id.in_(payload.users_id),
                MessAdmin.college_id == current_user.college_id
            )
            .returning(MessAdmin.user_id)
        )

        delete_mess_admins = await db.execute(mess_admins)
        deleted_ids = delete_mess_admins.scalars().all()
        if not deleted_ids:
            raise HTTPException(404, "Users not found")
        await db.commit()

        return deleted_ids


    elif payload.role == UserRole.college_admin:

            for attempt in range(MAX_RETRIES):
                try:
                    stmt = text("""
                                DELETE
                                FROM college_admin
                                WHERE id = ANY (:ids)
                                  AND college_id = :college_id
                                  AND (SELECT COUNT(*)
                                       FROM college_admin
                                       WHERE college_id = :college_id) > 1
                                    RETURNING id
                                """)

                    result = await db.execute(stmt, {
                        "ids": payload.users_id,
                        "college_id": current_user.college_id
                    })

                    deleted_ids = result.scalars().all()

                    await db.commit()

                    if not deleted_ids:
                        raise HTTPException(
                            400,
                            "Cannot delete! at least one admin must remain"
                        )

                    return deleted_ids

                except Exception as e:
                    await db.rollback()

                    if attempt == MAX_RETRIES - 1:
                        raise HTTPException(status_code=400, detail=str(e))

                    await asyncio.sleep(0.1)


    else:
        raise HTTPException(400, "Invalid role")

