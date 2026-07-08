from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from core.config import settings
from membership.repository import MembershipRepository, MembershipTypeRepository
from membership.schemas import MembershipTypeCreate, MembershipTypeUpdate
from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType


def get_active_membership(user_id: int, db: Session):
    tz = ZoneInfo(settings.timezone)
    hoy = datetime.now(tz).date()
    repo = MembershipRepository(db)
    membership = repo.get_active_by_user_id(user_id, hoy)
    if membership is None:
        raise ValueError("SIN_MEMBRESIA_ACTIVA")
    return membership


def consume_visit(membership_id: int, db: Session):
    repo = MembershipRepository(db)
    return repo.consume_visit(membership_id, db)


def consume_guest_slot(membership_id: int, db: Session):
    repo = MembershipRepository(db)
    return repo.consume_guest_slot(membership_id, db)


def get_membership_summary(membership, db: Session):
    tipo_repo = MembershipTypeRepository(db)
    tipo = tipo_repo.get_by_id(membership.tipo_id)
    return {
        "tipo": tipo.nombre if tipo else "Desconocido",
        "visitas_restantes": membership.visitas_restantes,
        "cupo_invitados_restantes": membership.cupo_invitados_restantes,
        "fecha_inicio": str(membership.fecha_inicio),
        "fecha_vencimiento": str(membership.fecha_vencimiento),
        "estado": membership.estado.value,
    }


def create_membership(user_id: int, tipo_id: int, db: Session) -> Membership:
    tz = ZoneInfo(settings.timezone)
    hoy = datetime.now(tz).date()

    tipo_repo = MembershipTypeRepository(db)
    tipo = tipo_repo.get_by_id(tipo_id)
    if tipo is None:
        raise ValueError("TIPO_NO_ENCONTRADO")

    membership = Membership(
        miembro_id=user_id,
        tipo_id=tipo_id,
        visitas_restantes=tipo.visitas_totales,
        cupo_invitados_restantes=tipo.cupo_invitados,
        fecha_inicio=hoy,
        fecha_vencimiento=hoy + timedelta(days=tipo.duracion_dias),
        estado=EstadoMembresia.activa,
    )
    repo = MembershipRepository(db)
    return repo.create(membership)


def list_membership_types(db: Session) -> list[MembershipType]:
    repo = MembershipTypeRepository(db)
    return repo.list_all()


def get_membership_type(tipo_id: int, db: Session) -> MembershipType:
    repo = MembershipTypeRepository(db)
    tipo = repo.get_by_id(tipo_id)
    if tipo is None:
        raise ValueError("TIPO_NO_ENCONTRADO")
    return tipo


def create_membership_type(data: MembershipTypeCreate, db: Session) -> MembershipType:
    repo = MembershipTypeRepository(db)
    tipo = MembershipType(
        nombre=data.nombre,
        precio_base=data.precio_base,
        visitas_totales=data.visitas_totales,
        cupo_invitados=data.cupo_invitados,
        duracion_dias=data.duracion_dias,
        activo=data.activo,
    )
    return repo.create(tipo)


def update_membership_type(tipo_id: int, data: MembershipTypeUpdate, db: Session) -> MembershipType:
    repo = MembershipTypeRepository(db)
    tipo = repo.get_by_id(tipo_id)
    if tipo is None:
        raise ValueError("TIPO_NO_ENCONTRADO")

    # RN-05: cannot deactivate if has active memberships
    if data.activo is False and tipo.activo is True:
        active_count = repo.count_active_memberships(tipo_id)
        if active_count > 0:
            raise ValueError("TIPO_CON_MEMBRESIAS_ACTIVAS")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tipo, field, value)

    repo.update(tipo)
    return tipo


def deactivate_membership_type(tipo_id: int, db: Session) -> MembershipType:
    repo = MembershipTypeRepository(db)
    tipo = repo.get_by_id(tipo_id)
    if tipo is None:
        raise ValueError("TIPO_NO_ENCONTRADO")

    # RN-05: cannot deactivate if has active memberships
    active_count = repo.count_active_memberships(tipo_id)
    if active_count > 0:
        raise ValueError("TIPO_CON_MEMBRESIAS_ACTIVAS")

    tipo.activo = False
    repo.update(tipo)
    return tipo


def delete_membership_type(tipo_id: int, db: Session) -> None:
    repo = MembershipTypeRepository(db)
    tipo = repo.get_by_id(tipo_id)
    if tipo is None:
        raise ValueError("TIPO_NO_ENCONTRADO")

    # RN-05: cannot delete if has active memberships
    active_count = repo.count_active_memberships(tipo_id)
    if active_count > 0:
        raise ValueError("TIPO_CON_MEMBRESIAS_ACTIVAS")

    repo.db.delete(tipo)
