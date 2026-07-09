"""
Servicio de checkin — orquesta el motor de validación de RN-01/RN-02/RN-08/RN-10
(spec/features/001-checkin-membresia-activa). Resuelve al usuario vía
members.service y valida/descuenta la membresía vía membership.service; nunca
consulta sus tablas directamente (regla de módulos, AGENTS.md).

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de checkin.
Ningún otro módulo debe importar checkin/repository.py directamente.
"""
import enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import membership.service as membership_service
import members.service as members_service
from checkin.repository import CheckinRepository
from membership.schemas import MembershipSummary
from models import CheckIn, ResultadoCheckin


class CheckinResultado(str, enum.Enum):
    exitoso = "exitoso"
    denegado = "denegado"


class UsuarioNoEncontradoError(Exception):
    """Cédula sin usuario registrado. La cortesía de primer día (005) todavía
    no está implementada, así que por ahora esto se trata como error 404 en
    el router — no es una decisión de negocio, es un límite explícito de
    alcance de 001 (ver "Fuera de alcance" en spec.md)."""


def checkin_member(cedula: str, db: Session):
    """Devuelve (CheckinResultado, mensaje, nombre, visitas_restantes)."""
    user = members_service.get_user_by_cedula(cedula, db)
    if user is None:
        raise UsuarioNoEncontradoError(cedula)

    repo = CheckinRepository(db)
    hoy = membership_service.hoy()

    # Filtro 1: ya tiene un CheckIn is_active=true de hoy → éxito directo,
    # sin reevaluar RN-01 ni descontar visita (spec.md, criterio "Filtro 1").
    if repo.exists_successful_checkin_today(user.id, hoy):
        resumen = membership_service.get_membership_summary(user.id, db)
        return _respuesta_exitosa(user.nombre, resumen)

    # Filtro 2: RN-01 (membresía activa + visitas_restantes > 0).
    membresia_activa = membership_service.get_active_membership(user.id, db)
    if membresia_activa is None:
        # Mensajería/razón de denegación detallada → 002-acceso-denegado (fuera
        # de alcance aquí); solo garantizamos que no se crea is_active=true.
        return (
            CheckinResultado.denegado,
            "ACCESO DENEGADO. Membresía vencida o sin visitas restantes.",
            user.nombre,
            None,
        )

    # Transacción única (RN-10): descuenta la visita e inserta el CheckIn, o
    # revierte ambos si algo falla. El commit/rollback lo hace este orquestador.
    try:
        membership_service.consume_visit(membresia_activa.id, db)
        repo.insert(
            CheckIn(
                usuario_id=user.id,
                resultado=ResultadoCheckin.exitoso,
                is_active=True,
            )
        )
        db.commit()
    except IntegrityError:
        # Condición de carrera: otro check-in concurrente del mismo socio ya
        # ganó el índice único parcial (usuario_id, día) para hoy — se resuelve
        # como Filtro 1 (éxito, sin volver a descontar), no como error.
        db.rollback()
        resumen = membership_service.get_membership_summary(user.id, db)
        return _respuesta_exitosa(user.nombre, resumen)
    except Exception:
        db.rollback()
        raise

    resumen = membership_service.get_membership_summary(user.id, db)
    return _respuesta_exitosa(user.nombre, resumen)


def _respuesta_exitosa(nombre: str | None, resumen: MembershipSummary | None):
    visitas = resumen.visitas_restantes if resumen else None
    return (
        CheckinResultado.exitoso,
        f"ACCESO PERMITIDO. Bienvenido/a {nombre}. Visitas restantes: {visitas}.",
        nombre,
        visitas,
    )
