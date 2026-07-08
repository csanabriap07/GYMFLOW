from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import require_role
from membership.schemas import (
    MembershipSummaryOut,
    MembershipTypeCreate,
    MembershipTypeUpdate,
    MembershipTypeOut,
)
from membership.service import (
    get_membership_summary,
    list_membership_types,
    get_membership_type,
    create_membership_type,
    update_membership_type,
    deactivate_membership_type,
    delete_membership_type,
)
from membership.repository import MembershipRepository
from members.service import get_user_by_cedula
from models.user import User

router = APIRouter(prefix="/membresias", tags=["membership"])


@router.get("/summary", response_model=MembershipSummaryOut)
def membership_summary(cedula: str = Query(...), db: Session = Depends(get_db)):
    try:
        user = get_user_by_cedula(cedula, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    tz = ZoneInfo(settings.timezone)
    ahora = datetime.now(tz)

    repo = MembershipRepository(db)
    membership = repo.get_active_by_user_id(user.id, ahora.date())

    if membership is None:
        return MembershipSummaryOut(
            tipo="Sin membresía",
            estado="vencida",
            visitas_restantes=0,
            cupo_invitados_restantes=0,
            fecha_inicio="-",
            fecha_vencimiento="-",
            proximo_pago="-",
        )

    summary = get_membership_summary(membership, db)
    return MembershipSummaryOut(
        tipo=summary["tipo"],
        estado=summary["estado"],
        visitas_restantes=summary["visitas_restantes"],
        cupo_invitados_restantes=summary["cupo_invitados_restantes"],
        fecha_inicio=summary["fecha_inicio"],
        fecha_vencimiento=summary["fecha_vencimiento"],
        proximo_pago=summary["fecha_vencimiento"],
    )


@router.get("/tipos", response_model=list[MembershipTypeOut])
def list_tipos(db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    return list_membership_types(db)


@router.get("/tipos/{tipo_id}", response_model=MembershipTypeOut)
def get_tipo(tipo_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    try:
        return get_membership_type(tipo_id, db)
    except ValueError:
        raise HTTPException(status_code=404, detail="Tipo de membresía no encontrado")


@router.post("/tipos", response_model=MembershipTypeOut, status_code=201)
def create_tipo(data: MembershipTypeCreate, db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    tipo = create_membership_type(data, db)
    db.commit()
    return tipo


@router.put("/tipos/{tipo_id}", response_model=MembershipTypeOut)
def update_tipo(tipo_id: int, data: MembershipTypeUpdate, db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    try:
        tipo = update_membership_type(tipo_id, data, db)
        db.commit()
        return tipo
    except ValueError as e:
        if str(e) == "TIPO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail="Tipo de membresía no encontrado")
        if str(e) == "TIPO_CON_MEMBRESIAS_ACTIVAS":
            raise HTTPException(status_code=409, detail="No se puede desactivar: tiene membresías activas vinculadas")
        raise


@router.patch("/tipos/{tipo_id}/desactivar", response_model=MembershipTypeOut)
def deactivate_tipo(tipo_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    try:
        tipo = deactivate_membership_type(tipo_id, db)
        db.commit()
        return tipo
    except ValueError as e:
        if str(e) == "TIPO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail="Tipo de membresía no encontrado")
        if str(e) == "TIPO_CON_MEMBRESIAS_ACTIVAS":
            raise HTTPException(status_code=409, detail="No se puede desactivar: tiene membresías activas vinculadas")
        raise


@router.delete("/tipos/{tipo_id}", status_code=204)
def delete_tipo(tipo_id: int, db: Session = Depends(get_db), _: User = Depends(require_role("administrador"))):
    try:
        delete_membership_type(tipo_id, db)
        db.commit()
    except ValueError as e:
        if str(e) == "TIPO_NO_ENCONTRADO":
            raise HTTPException(status_code=404, detail="Tipo de membresía no encontrado")
        if str(e) == "TIPO_CON_MEMBRESIAS_ACTIVAS":
            raise HTTPException(status_code=409, detail="No se puede eliminar: tiene membresías activas vinculadas")
        raise
