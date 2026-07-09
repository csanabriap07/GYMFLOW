"""
Tests de checkin/service.py contra los criterios de aceptación de
spec/features/001-checkin-membresia-activa/spec.md.
"""
import threading
from datetime import date, timedelta

import pytest
from sqlalchemy.orm import sessionmaker

from checkin.service import CheckinResultado, checkin_member
from core.database import engine
from models import CheckIn, EstadoMembresia, EstadoUsuario, Membership, MembershipType, RolUsuario, User


def _crear_socio(db, visitas_restantes=5, dias_vencimiento=30):
    tipo = MembershipType(
        nombre="Mensual",
        precio_base=50000,
        visitas_totales=30,
        cupo_invitados=1,
        duracion_dias=30,
        activo=True,
    )
    db.add(tipo)
    db.flush()

    user = User(
        cedula="1000000001",
        nombre="Ana Pérez",
        rol=RolUsuario.miembro,
        estado=EstadoUsuario.activo,
    )
    db.add(user)
    db.flush()

    membership = Membership(
        miembro_id=user.id,
        tipo_id=tipo.id,
        visitas_restantes=visitas_restantes,
        cupo_invitados_restantes=tipo.cupo_invitados,
        fecha_inicio=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=dias_vencimiento),
        estado=EstadoMembresia.activa,
    )
    db.add(membership)
    db.commit()
    return user, membership


def test_checkin_exitoso_descuenta_exactamente_una_visita(db):
    user, membership = _crear_socio(db, visitas_restantes=5)

    resultado, mensaje, nombre, visitas_restantes = checkin_member(user.cedula, db)

    assert resultado == CheckinResultado.exitoso
    assert nombre == "Ana Pérez"
    assert visitas_restantes == 4
    assert "Ana Pérez" in mensaje

    db.refresh(membership)
    assert membership.visitas_restantes == 4


def test_segundo_checkin_mismo_dia_no_descuenta_de_nuevo(db):
    """Filtro 1: un reingreso el mismo día es exitoso pero no descuenta ni
    reevalúa RN-01, y no crea un segundo CheckIn is_active=true."""
    user, membership = _crear_socio(db, visitas_restantes=5)

    checkin_member(user.cedula, db)
    resultado, _, _, visitas_restantes = checkin_member(user.cedula, db)

    assert resultado == CheckinResultado.exitoso
    assert visitas_restantes == 4

    db.refresh(membership)
    assert membership.visitas_restantes == 4

    activos = (
        db.query(CheckIn)
        .filter(CheckIn.usuario_id == user.id, CheckIn.is_active.is_(True))
        .all()
    )
    assert len(activos) == 1


def test_sin_visitas_restantes_deniega_sin_crear_checkin_activo(db):
    user, membership = _crear_socio(db, visitas_restantes=0)

    resultado, _, _, visitas_restantes = checkin_member(user.cedula, db)

    assert resultado == CheckinResultado.denegado
    assert visitas_restantes is None

    db.refresh(membership)
    assert membership.visitas_restantes == 0
    assert db.query(CheckIn).filter(CheckIn.is_active.is_(True)).count() == 0


def test_membresia_vencida_deniega(db):
    user, membership = _crear_socio(db, visitas_restantes=5, dias_vencimiento=-1)

    resultado, _, _, _ = checkin_member(user.cedula, db)

    assert resultado == CheckinResultado.denegado
    db.refresh(membership)
    assert membership.visitas_restantes == 5


def test_rollback_no_descuenta_si_falla_a_mitad_de_transaccion(db, monkeypatch):
    """RN-10: un fallo entre el descuento y el insert no deja la visita
    descontada sin su CheckIn correspondiente."""
    user, membership = _crear_socio(db, visitas_restantes=5)

    def _insert_roto(self, checkin):
        raise RuntimeError("fallo simulado a mitad de la transacción")

    monkeypatch.setattr("checkin.repository.CheckinRepository.insert", _insert_roto)

    with pytest.raises(RuntimeError):
        checkin_member(user.cedula, db)

    db.rollback()
    db.refresh(membership)
    assert membership.visitas_restantes == 5
    assert db.query(CheckIn).count() == 0


def test_diez_checkins_concurrentes_no_descuentan_de_mas(db):
    """RNF concurrencia: ≥10 check-ins simultáneos del mismo socio el mismo
    día descuentan exactamente 1 visita en total (índice único parcial +
    SELECT ... FOR UPDATE)."""
    user, membership = _crear_socio(db, visitas_restantes=5)
    membership_id = membership.id
    cedula = user.cedula

    resultados: list[CheckinResultado] = []
    lock = threading.Lock()

    def _worker():
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            resultado, *_ = checkin_member(cedula, session)
            with lock:
                resultados.append(resultado)
        finally:
            session.close()

    hilos = [threading.Thread(target=_worker) for _ in range(10)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()

    assert len(resultados) == 10
    assert all(r == CheckinResultado.exitoso for r in resultados)

    db.expire_all()
    membership_final = db.get(Membership, membership_id)
    assert membership_final.visitas_restantes == 4

    activos = (
        db.query(CheckIn)
        .filter(CheckIn.usuario_id == user.id, CheckIn.is_active.is_(True))
        .count()
    )
    assert activos == 1
