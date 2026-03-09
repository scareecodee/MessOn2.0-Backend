from fastapi import Depends, HTTPException, status
from app.utils.userRole import UserRole
from app.models.user.userModel import User
from app.security.dependencies.getCurrentUser import get_current_user


def get_current_role(role: UserRole):
    def role_check(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(403, "Access denied")
        return current_user
    return role_check