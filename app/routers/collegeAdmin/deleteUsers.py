from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.student.studentModel import Student
from app.services.deleteUsersService import delete_users
from app.models.user.userModel import User
from app.security.dependencies.getCurrentRole import get_current_role
from app.db.session import get_db
from app.schemas.student.deleteUsers import DeleteUsers
from app.utils.userRole import UserRole

router = APIRouter(
    prefix="/delete",
    tags=["College Admins Mess Deletion Operations"]
)

@router.delete("/users")
async def delete_students(
    payload: DeleteUsers,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_role([UserRole.college_admin]))
):
    if payload.role==UserRole.student:
        deleted_ids = await delete_users(payload,db,current_user)
        if not deleted_ids:
            raise HTTPException(404, "Student not found")
        return {
            "message": f"{len(deleted_ids)} Students deleted successfully",
        }

    if payload.role==UserRole.mess_admin:
        deleted_ids = await delete_users(payload,db,current_user)
        if not deleted_ids:
            raise HTTPException(404, "Mess Admin not found")
        return {
            "message": f"{len(deleted_ids)} mess admins deleted successfully"        }


    else :
        deleted_ids = await delete_users(payload, db, current_user)
        if not deleted_ids:
            raise HTTPException(404, "College not found")

        return {
            "message": f"{len(deleted_ids)} College Admins deleted successfully",
        }
