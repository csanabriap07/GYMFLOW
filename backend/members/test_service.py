"""
Tests de members/service.py contra los criterios de aceptación de
HU-07 — Gestión de usuarios (CRUD de usuarios y RN-07).
"""
from decimal import Decimal

import pytest

from members.service import (
    CedulaYaRegistradaError,
    EmailYaRegistradoError,
    UsuarioNoEncontradoError,
    anonymize_user,
    assign_membership,
    create_user,
    get_membership_history,
    list_users,
    puede_asignar_rol,
    renew_membership,
    update_user,
)
from models import CheckIn, EstadoUsuario, MembershipType, ResultadoCheckin, RolUsuario


def _crear_tipo(db) -> MembershipType:
    tipo = MembershipType(
        nombre="Mensual", precio_base=Decimal("50000"), visitas_totales=30,
        cupo_invitados=1, duracion_dias=30, activo=True,
    )
    db.add(tipo)
    db.flush()
    return tipo


def test_create_user_miembro_sin_password(db):
    user = create_user("123", "Juan", "juan@test.com", RolUsuario.miembro, EstadoUsuario.activo, None, db)
    assert user.id is not None
    assert user.password_hash is None


def test_create_user_empleado_requiere_password_hasheada(db):
    user = create_user(
        "456", "Laura", "laura@test.com", RolUsuario.empleado, EstadoUsuario.activo, "clave123", db
    )
    assert user.password_hash is not None
    assert user.password_hash != "clave123"


def test_create_user_cedula_duplicada(db):
    create_user("789", "Pedro", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)
    with pytest.raises(CedulaYaRegistradaError):
        create_user("789", "Otro", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)


def test_create_user_email_duplicado(db):
    create_user("1", "Pedro", "dup@test.com", RolUsuario.miembro, EstadoUsuario.activo, None, db)
    with pytest.raises(EmailYaRegistradoError):
        create_user("2", "Otro", "dup@test.com", RolUsuario.miembro, EstadoUsuario.activo, None, db)


def test_update_user_cambia_campos(db):
    user = create_user("1", "Pedro", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)
    actualizado = update_user(user.id, db, nombre="Pedro Actualizado")
    assert actualizado.nombre == "Pedro Actualizado"


def test_update_user_inexistente(db):
    with pytest.raises(UsuarioNoEncontradoError):
        update_user(9999, db, nombre="X")


def test_list_users(db):
    create_user("1", "A", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)
    create_user("2", "B", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)
    assert len(list_users(db)) == 2


def test_anonymize_user_borra_pii_pero_conserva_id(db):
    user = create_user("111", "Carlos", "carlos@test.com", RolUsuario.miembro, EstadoUsuario.activo, None, db)
    user_id = user.id

    anonimizado = anonymize_user(user_id, db)

    assert anonimizado.id == user_id
    assert anonimizado.cedula is None
    assert anonimizado.nombre is None
    assert anonimizado.email is None
    assert anonimizado.estado == EstadoUsuario.inactivo


def test_anonymize_user_preserva_checkins_historicos(db):
    user = create_user("222", "Diana", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)
    checkin = CheckIn(usuario_id=user.id, resultado=ResultadoCheckin.exitoso, is_active=True)
    db.add(checkin)
    db.commit()

    anonymize_user(user.id, db)

    conservado = db.query(CheckIn).filter(CheckIn.usuario_id == user.id).first()
    assert conservado is not None
    assert conservado.id == checkin.id


def test_assign_and_renew_membership_delegan_en_membership_service(db):
    tipo = _crear_tipo(db)
    user = create_user("333", "Elena", None, RolUsuario.miembro, EstadoUsuario.activo, None, db)

    primera = assign_membership(user.id, tipo.id, Decimal("50000"), "efectivo", db)
    assert primera.miembro_id == user.id

    segunda = renew_membership(user.id, tipo.id, Decimal("50000"), None, db)
    assert segunda.id != primera.id

    historial = get_membership_history(user.id, db)
    assert len(historial) == 2


def test_assign_membership_usuario_inexistente(db):
    tipo = _crear_tipo(db)
    with pytest.raises(UsuarioNoEncontradoError):
        assign_membership(9999, tipo.id, Decimal("50000"), None, db)


# --- puede_asignar_rol: quién puede crear/ascender a qué rol (hallazgo posterior a HU-07) ---


def test_puede_asignar_rol_administrador_solo_administrador():
    assert puede_asignar_rol(RolUsuario.administrador, set(), RolUsuario.administrador) is True
    assert puede_asignar_rol(RolUsuario.empleado, set(), RolUsuario.administrador) is False
    # Ni con el permiso individual de empleado alcanza para crear otro admin.
    assert (
        puede_asignar_rol(
            RolUsuario.empleado, {"members.asignar_rol_empleado"}, RolUsuario.administrador
        )
        is False
    )


def test_puede_asignar_rol_empleado_admin_o_permiso_individual():
    assert puede_asignar_rol(RolUsuario.administrador, set(), RolUsuario.empleado) is True
    assert puede_asignar_rol(RolUsuario.empleado, set(), RolUsuario.empleado) is False
    assert (
        puede_asignar_rol(
            RolUsuario.empleado, {"members.asignar_rol_empleado"}, RolUsuario.empleado
        )
        is True
    )


def test_puede_asignar_rol_miembro_invitado_sin_restriccion():
    assert puede_asignar_rol(RolUsuario.empleado, set(), RolUsuario.miembro) is True
    assert puede_asignar_rol(RolUsuario.empleado, set(), RolUsuario.invitado) is True
