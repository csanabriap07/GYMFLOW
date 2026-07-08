from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import require_role
from core.qr import decode_qr
from members.schemas import UserCreate, UserUpdate, UserOut
from members import service as members_service

router = APIRouter(prefix="/usuarios", tags=["members"])


@router.get("/search", dependencies=[Depends(require_role("administrador", "empleado"))])
def search_users(q: str = Query(...), db: Session = Depends(get_db)):
    users = members_service.search_users(q, db)
    return [UserOut.model_validate(u) for u in users]


@router.get("", dependencies=[Depends(require_role("administrador", "empleado"))])
def list_users(db: Session = Depends(get_db)):
    users = members_service.list_users(db)
    return [UserOut.model_validate(u) for u in users]


@router.post("", dependencies=[Depends(require_role("administrador"))], response_model=UserOut)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    try:
        user = members_service.create_user(body.model_dump(), db)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserOut.model_validate(user)


@router.get("/{user_id}", dependencies=[Depends(require_role("administrador", "empleado"))], response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
        user = members_service.get_user(user_id, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UserOut.model_validate(user)


@router.put("/{user_id}", dependencies=[Depends(require_role("administrador"))], response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = members_service.update_user(user_id, body.model_dump(exclude_unset=True), db)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserOut.model_validate(user)


@router.delete("/{user_id}", dependencies=[Depends(require_role("administrador"))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        members_service.anonymize_user(user_id, db)
        db.commit()
    except ValueError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"detail": "Usuario eliminado"}


@router.post("/{user_id}/membresia", dependencies=[Depends(require_role("administrador"))])
def assign_membership(user_id: int, tipo_id: int, db: Session = Depends(get_db)):
    try:
        membership = members_service.assign_membership(user_id, tipo_id, db)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "id": membership.id,
        "miembro_id": membership.miembro_id,
        "tipo_id": membership.tipo_id,
        "visitas_restantes": membership.visitas_restantes,
        "cupo_invitados_restantes": membership.cupo_invitados_restantes,
        "fecha_inicio": str(membership.fecha_inicio),
        "fecha_vencimiento": str(membership.fecha_vencimiento),
        "estado": membership.estado.value,
    }
