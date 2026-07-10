"""
Tests de auth/service.py contra los criterios de aceptación de
spec/features/003-autenticacion-segura/spec.md.
"""
import pytest

from auth.conftest import PASSWORD, otorgar_permiso
from auth.service import (
    CredencialesInvalidasError,
    PermisoInexistenteError,
    get_user_permissions,
    grant_permission,
    list_permissions,
    list_permissions_catalog,
    login,
    revoke_permission,
)
from core.security import decode_access_token, hash_password
from members.service import UsuarioNoEncontradoError
from models import EstadoUsuario, RolUsuario, User


def test_login_credenciales_validas_retorna_token_con_rol_y_exp(db, empleado):
    token, rol, permisos = login(empleado.email, PASSWORD, db)

    assert rol == RolUsuario.empleado
    assert permisos == set()
    payload = decode_access_token(token)
    assert payload["rol"] == RolUsuario.empleado.value
    assert payload["sub"] == str(empleado.id)
    assert "exp" in payload


def test_login_devuelve_los_permisos_otorgados_al_usuario(db, empleado):
    otorgar_permiso(db, empleado.id, "checkin.desbloquear_dispositivo")

    _, _, permisos = login(empleado.email, PASSWORD, db)

    assert permisos == {"checkin.desbloquear_dispositivo"}


def test_login_password_incorrecta_lanza_credenciales_invalidas(db, empleado):
    with pytest.raises(CredencialesInvalidasError):
        login(empleado.email, "otra-clave", db)


def test_login_email_inexistente_lanza_credenciales_invalidas(db):
    with pytest.raises(CredencialesInvalidasError):
        login("no-existe@gymflow.test", PASSWORD, db)


def test_login_rol_miembro_no_puede_loguearse(db):
    miembro = User(
        nombre="Socio Test",
        email="socio@gymflow.test",
        rol=RolUsuario.miembro,
        estado=EstadoUsuario.activo,
        password_hash=hash_password(PASSWORD),
    )
    db.add(miembro)
    db.commit()

    with pytest.raises(CredencialesInvalidasError):
        login(miembro.email, PASSWORD, db)


def test_login_usuario_inactivo_no_puede_loguearse(db, empleado_inactivo):
    with pytest.raises(CredencialesInvalidasError):
        login(empleado_inactivo.email, PASSWORD, db)


def test_login_con_hash_de_formato_irreconocible_lanza_credenciales_invalidas(db, empleado):
    # Guard contra un hasher legacy (ej. bcrypt de una migración de librería
    # de hashing) que pwdlib no reconoce: debe fallar como credenciales
    # inválidas, no tumbar el request con un 500 (core/security.py).
    empleado.password_hash = "$2b$12$noeselformatoqueentiendepwdlib"
    db.commit()

    with pytest.raises(CredencialesInvalidasError):
        login(empleado.email, PASSWORD, db)


def test_password_se_almacena_hasheada(db, empleado):
    assert empleado.password_hash != PASSWORD
    assert empleado.password_hash.startswith("$argon2")


def test_get_user_permissions_devuelve_permisos_otorgados(db, empleado):
    assert get_user_permissions(empleado.id, db) == set()

    otorgar_permiso(db, empleado.id, "checkin.desbloquear_dispositivo")

    assert get_user_permissions(empleado.id, db) == {"checkin.desbloquear_dispositivo"}


def test_grant_permission_otorga_y_es_idempotente(db, empleado):
    grant_permission(empleado.id, "membership.renovar", db)
    grant_permission(empleado.id, "membership.renovar", db)  # no duplica

    permisos = list_permissions(empleado.id, db)
    assert [p.codigo for p in permisos] == ["membership.renovar"]


def test_grant_permission_codigo_inexistente(db, empleado):
    with pytest.raises(PermisoInexistenteError):
        grant_permission(empleado.id, "no.existe", db)


def test_grant_permission_usuario_inexistente(db):
    with pytest.raises(UsuarioNoEncontradoError):
        grant_permission(9999, "membership.renovar", db)


def test_revoke_permission_quita_el_permiso(db, empleado):
    grant_permission(empleado.id, "membership.renovar", db)
    revoke_permission(empleado.id, "membership.renovar", db)

    assert list_permissions(empleado.id, db) == []


def test_list_permissions_catalog_devuelve_todo_el_catalogo(db):
    codigos = {p.codigo for p in list_permissions_catalog(db)}

    # Sembrados por las migraciones de 003/004 — el catálogo completo, no
    # solo lo otorgado a un usuario en particular.
    assert {
        "checkin.ver_dispositivos_bloqueados",
        "checkin.desbloquear_dispositivo",
        "membership.renovar",
        "members.asignar_rol_empleado",
    }.issubset(codigos)
