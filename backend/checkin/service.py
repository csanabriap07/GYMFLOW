from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from checkin.repository import CheckinRepository
from core.config import settings
from models.checkin import CheckIn, ResultadoCheckin


def get_attendance(fecha_inicio: date, fecha_fin: date, db: Session) -> list[dict]:
    """Devuelve filas de CheckIn en el rango dado (consulta sobre la propia tabla del módulo)."""
    from models.user import User

    checkins = (
        db.query(CheckIn)
        .filter(CheckIn.fecha >= fecha_inicio, CheckIn.fecha <= fecha_fin)
        .order_by(CheckIn.fecha_hora.asc())
        .all()
    )

    rows = []
    for ci in checkins:
        user = db.query(User).filter(User.id == ci.usuario_id).first()
        rows.append({
            "id": ci.id,
            "usuario_id": ci.usuario_id,
            "usuario_nombre": user.nombre if user else "Desconocido",
            "usuario_cedula": user.cedula if user else "-",
            "fecha_hora": ci.fecha_hora.isoformat(),
            "resultado": ci.resultado.value,
            "razon": ci.razon_denegacion if hasattr(ci, "razon_denegacion") else None,
        })
    return rows


def first_day_courtesy(cedula: str, device_id: str, db: Session) -> dict:
    tz = ZoneInfo(settings.timezone)
    ahora = datetime.now(tz)
    hoy = ahora.date()

    checkin_repo = CheckinRepository(db)

    from members.service import has_used_courtesy, create_prospect

    if has_used_courtesy(cedula, db):
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "CORTESIA_YA_UTILIZADA",
            "mensaje": "Cortesía de primer día ya utilizada. Acérquese a recepción para afiliarse.",
        }

    user = create_prospect(cedula, db)

    checkin = CheckIn(
        usuario_id=user.id,
        fecha_hora=ahora,
        fecha=hoy,
        resultado=ResultadoCheckin.exitoso,
    )
    checkin_repo.insert(checkin)
    checkin_repo.reset_attempts(device_id)
    db.flush()

    return {
        "resultado": "exitoso",
        "mensaje": "¡Bienvenido/a! Este es tu acceso gratuito de cortesía.",
        "nombre": user.nombre or "Prospecto",
        "visitas_restantes": None,
        "membresia": None,
        "cortesia": True,
    }


def checkin_guest(cedula_invitado: str, cedula_titular: str, device_id: str, db: Session) -> dict:
    tz = ZoneInfo(settings.timezone)
    ahora = datetime.now(tz)
    hoy = ahora.date()

    checkin_repo = CheckinRepository(db)

    if checkin_repo.is_locked(device_id, ahora):
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "DISPOSITIVO_BLOQUEADO",
            "mensaje": "ACCESO DENEGADO. Demasiados intentos fallidos.",
            "bloqueado_hasta": str(ahora + timedelta(minutes=20)),
        }

    from members.service import get_user_by_cedula

    try:
        titular = get_user_by_cedula(cedula_titular, db)
    except ValueError:
        return {
            "resultado": "denegado",
            "razon": "TITULAR_NO_ENCONTRADO",
            "mensaje": "Socio titular no encontrado.",
        }

    from membership.service import get_active_membership, consume_guest_slot, get_membership_summary

    try:
        membership = get_active_membership(titular.id, db)
    except ValueError:
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "TITULAR_SIN_MEMBRESIA",
            "mensaje": "El socio titular no tiene membresía activa.",
        }

    if membership.cupo_invitados_restantes <= 0:
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "SIN_CUPOS_INVITADOS",
            "mensaje": "El socio titular no tiene cupos de invitado disponibles.",
        }

    last_checkin = checkin_repo.get_last_successful_member_checkin(titular.id, device_id)
    if last_checkin is None:
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "TITULAR_NO_INGRESO",
            "mensaje": "El socio titular debe ingresar primero.",
        }

    from members.service import get_guest_by_cedula, create_guest

    guest = get_guest_by_cedula(cedula_invitado, db)
    if guest is None:
        guest = create_guest(cedula_invitado, titular.id, db)

    consume_guest_slot(membership.id, db)

    checkin = CheckIn(
        usuario_id=guest.id,
        fecha_hora=ahora,
        fecha=hoy,
        resultado=ResultadoCheckin.exitoso,
    )
    checkin_repo.insert(checkin)
    checkin_repo.reset_attempts(device_id)
    db.flush()

    return {
        "resultado": "exitoso",
        "mensaje": f"Bienvenido/a. El socio {titular.nombre} tiene ahora {membership.cupo_invitados_restantes} invitaciones restantes.",
        "nombre": guest.nombre or "Invitado",
        "visitas_restantes": None,
        "cupos_invitados": membership.cupo_invitados_restantes,
        "membresia": None,
    }


def checkin_member(cedula: str, device_id: str, db: Session) -> dict:
    tz = ZoneInfo(settings.timezone)
    ahora = datetime.now(tz)
    hoy = ahora.date()

    checkin_repo = CheckinRepository(db)

    if checkin_repo.is_locked(device_id, ahora):
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "DISPOSITIVO_BLOQUEADO",
            "mensaje": "ACCESO DENEGADO. Demasiados intentos fallidos. Intente más tarde.",
            "bloqueado_hasta": str(ahora + timedelta(minutes=20)),
        }

    from members.service import get_user_by_cedula

    try:
        user = get_user_by_cedula(cedula, db)
    except ValueError:
        return first_day_courtesy(cedula, device_id, db)

    if checkin_repo.exists_successful_today(user.id, hoy):
        if user.cortesia_usada:
            return {
                "resultado": "denegado",
                "razon": "CORTESIA_YA_UTILIZADA",
                "mensaje": "Cortesía de primer día ya utilizada. Acérquese a recepción para afiliarse.",
            }
        return {
            "resultado": "denegado",
            "razon": "YA_INGRESO_HOY",
            "mensaje": "ACCESO DENEGADO. Ya registró su ingreso hoy.",
        }

    from membership.service import get_active_membership, consume_visit, get_membership_summary

    try:
        membership = get_active_membership(user.id, db)
    except ValueError:
        checkin_repo.register_denied(device_id, ahora)
        db.flush()
        return {
            "resultado": "denegado",
            "razon": "SIN_MEMBRESIA_ACTIVA",
            "mensaje": "ACCESO DENEGADO. Membresía vencida o sin visitas disponibles.",
        }

    consume_visit(membership.id, db)

    checkin = CheckIn(
        usuario_id=user.id,
        fecha_hora=ahora,
        fecha=hoy,
        resultado=ResultadoCheckin.exitoso,
    )
    checkin_repo.insert(checkin)

    checkin_repo.reset_attempts(device_id)
    db.flush()

    summary = get_membership_summary(membership, db)

    return {
        "resultado": "exitoso",
        "mensaje": f"ACCESO PERMITIDO. Bienvenido/a {user.nombre}. Visitas restantes: {membership.visitas_restantes}",
        "nombre": user.nombre,
        "visitas_restantes": membership.visitas_restantes,
        "membresia": summary,
    }
