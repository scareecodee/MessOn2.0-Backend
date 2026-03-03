from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.models.mess.messAdminModel import MessAdmin
from app.models.superAdmin.superAdminModel import SuperAdmin
from app.schemas.mess.messAdminSchema import (
    MessAdminCreate,
    MessAdminUpdate,
    MessAdminResponse
)

router = APIRouter(
    prefix="/admin/mess-admins",
    tags=["Mess Admin Management"]
)

@router.post("/create", response_model=MessAdminResponse)
def create_mess_admin(
    payload: MessAdminCreate,
    db: Session = Depends(get_db),

):
    existingMessAdmin = db.query(MessAdmin).filter(
        MessAdmin.email == payload.email
    ).first()

    if existingMessAdmin:
        raise HTTPException(
            status_code=400,
            detail=f"Mess admin with {payload.email} already exists"
        )
    # if not payload.is_active:
    #      raise HTTPException(
    #         status_code=400,
    #         detail=f"Mess admin {payload.name} is not active"
    #     )
    admin = MessAdmin(
        email=payload.email,
        name=payload.name,
        is_active=payload.is_active

    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin

@router.put("/update/{admin_id}", response_model=MessAdminResponse)
def update_mess_admin(
    admin_id: UUID,
    payload: MessAdminUpdate,
    db: Session = Depends(get_db),
   
):
    admin = db.query(MessAdmin).filter(
        MessAdmin.id == admin_id
    ).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Mess admin not found")
    
    if payload.email is not None and payload.email != admin.email:
        existing = db.query(MessAdmin).filter(
            MessAdmin.email == payload.email
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already in use by another admin"
            )

        admin.email = payload.email

    
    if payload.name is not None:
        admin.name = payload.name

    if payload.is_active is not None:
        admin.is_active = payload.is_active

    # if payload.picture is not None:
    #     admin.picture = payload.picture

    db.commit()
    db.refresh(admin)

    return admin

@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mess_admin(
    admin_id: UUID,
    db: Session = Depends(get_db),
    
):
    admin = db.query(MessAdmin).filter(
        MessAdmin.id == admin_id
    ).first()

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Mess admin not found"
        )

    db.delete(admin)
    db.commit()

    return None


@router.post("/create", response_model=MessAdminResponse)
def create_mess_admin(
        payload: SuperAdmin,
        db: Session = Depends(get_db),

):
    existingSuperAdmin = db.query(SuperAdmin).filter(
        MessAdmin.email == payload.email
    ).first()

    if existingSuperAdmin:
        raise HTTPException(
            status_code=400,
            detail=f"Mess admin with {payload.email} already exists"
        )
    # if not payload.is_active:
    #      raise HTTPException(
    #         status_code=400,
    #         detail=f"Mess admin {payload.name} is not active"
    #     )
    admin = SuperAdmin(
        email=payload.email,
        name=payload.name,
        is_active=payload.is_active

    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin