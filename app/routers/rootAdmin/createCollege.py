from fastapi import Depends,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.college.collegeModel import College
from app.schemas.rootAdmin.createCollege import CollegeCreate
from app.security.dependencies.getCurrentRootAdmin import get_current_root_admin

router = APIRouter(
    tags=["Create College By RootAdmin"],
)

@router.post("/colleges")
async def create_college(
    payload: CollegeCreate,
    root = Depends(get_current_root_admin),
    db: AsyncSession = Depends(get_db)
):
    college = College(
        name=payload.name,
        domain=payload.domain,
        status=True
    )

    db.add(college)
    await db.commit()
    await db.refresh(college)

    return college