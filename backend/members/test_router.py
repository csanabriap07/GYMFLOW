"""
Tests HTTP de members/router.py contra los criterios de aceptación de
HU-07 — Gestión de usuarios.
"""
from decimal import Decimal

from fastapi.testclient import TestClient

from auth.conftest import _crear_staff, otorgar_permiso
from core.security import create_access_token
from main import app
from models import EstadoUsuario, MembershipType, RolUsuario

client = TestClient(app)


def _crear_tipo(db) -> MembershipType:
    tipo = MembershipType(
        nombre="Mensual", precio_base=Decimal("50000"), visitas_totales=30,
        cupo_invitados=1, duracion_dias=30, activo=True,
    )
    db.add(tipo)
    db.commit()
    return tipo


def _token_empleado(db, permisos: tuple[str, ...] = ()) -> str:
    """Empleado con `members.gestionar_usuarios` siempre otorgado (es la
    precondición para poder hacer CRUD de usuarios en la mayoría de estos
    tests) + lo que se pida extra en `permisos`. Los tests que prueban
    específicamente la AUSENCIA de `members.gestionar_usuarios` crean su
    propio empleado a mano en vez de usar este helper."""
    empleado = _crear_staff(db, RolUsuario.empleado, "empleado-004@gymflow.test")
    otorgar_permiso(db, empleado.id, "members.gestionar_usuarios")
    for codigo in permisos:
        otorgar_permiso(db, empleado.id, codigo)
    return create_access_token({"sub": str(empleado.id), "rol": "empleado"})


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_crear_usuario_sin_token_401(db):
    resp = client.post("/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"})
    assert resp.status_code == 401


def test_crear_usuario_como_empleado_201(db):
    token = _token_empleado(db)
    resp = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "miembro"},
        headers=_headers(token),
    )
    assert resp.status_code == 201
    assert resp.json()["cedula"] == "1"
    assert "password_hash" not in resp.json()


def test_crear_usuario_empleado_sin_password_falla_validacion(db):
    token = _token_empleado(db)
    resp = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "empleado"},
        headers=_headers(token),
    )
    assert resp.status_code == 422


def test_crear_usuario_cedula_duplicada_409(db):
    token = _token_empleado(db)
    client.post("/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token))
    resp = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "Y", "rol": "miembro"}, headers=_headers(token)
    )
    assert resp.status_code == 409


def test_listar_y_obtener_usuario(db):
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    listado = client.get("/usuarios", headers=_headers(token))
    assert listado.status_code == 200
    # 2: el propio empleado que hace la request + el usuario recién creado.
    assert len(listado.json()) == 2

    detalle = client.get(f"/usuarios/{creado['id']}", headers=_headers(token))
    assert detalle.status_code == 200
    assert detalle.json()["id"] == creado["id"]


def test_obtener_usuario_inexistente_404(db):
    token = _token_empleado(db)
    resp = client.get("/usuarios/9999", headers=_headers(token))
    assert resp.status_code == 404


def test_editar_usuario(db):
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    resp = client.put(
        f"/usuarios/{creado['id']}", json={"nombre": "Nuevo nombre"}, headers=_headers(token)
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Nuevo nombre"


def test_eliminar_usuario_anonimiza(db):
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "email": "x@test.com", "rol": "miembro"},
        headers=_headers(token),
    ).json()

    resp = client.delete(f"/usuarios/{creado['id']}", headers=_headers(token))
    assert resp.status_code == 200
    assert resp.json()["cedula"] is None
    assert resp.json()["estado"] == EstadoUsuario.inactivo.value


def test_asignar_membresia_primera_vez(db):
    tipo = _crear_tipo(db)
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    resp = client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000", "nota": "efectivo"},
        headers=_headers(token),
    )
    assert resp.status_code == 200
    assert resp.json()["vigente"] is True


def test_asignar_membresia_dos_veces_409(db):
    tipo = _crear_tipo(db)
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()
    client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )

    resp = client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )
    assert resp.status_code == 409


def test_renovar_sin_permiso_membership_renovar_403(db):
    tipo = _crear_tipo(db)
    token = _token_empleado(db)  # sin el permiso membership.renovar
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()
    client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )

    resp = client.post(
        f"/usuarios/{creado['id']}/membresias/renovar",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )
    assert resp.status_code == 403


def test_renovar_con_permiso_membership_renovar_200(db):
    tipo = _crear_tipo(db)
    empleado = _crear_staff(db, RolUsuario.empleado, "empleado-004@gymflow.test")
    otorgar_permiso(db, empleado.id, "members.gestionar_usuarios")
    token = create_access_token({"sub": str(empleado.id), "rol": "empleado"})
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()
    client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )

    otorgar_permiso(db, empleado.id, "membership.renovar")
    resp = client.post(
        f"/usuarios/{creado['id']}/membresias/renovar",
        json={"tipo_id": tipo.id, "monto": "60000"},
        headers=_headers(token),
    )
    assert resp.status_code == 200


def test_renovar_sin_membresia_previa_409(db):
    tipo = _crear_tipo(db)
    token = _token_empleado(db, permisos=("membership.renovar",))
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    resp = client.post(
        f"/usuarios/{creado['id']}/membresias/renovar",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )
    assert resp.status_code == 409


def test_administrador_puede_renovar_sin_permiso_individual(db):
    tipo = _crear_tipo(db)
    admin = _crear_staff(db, RolUsuario.administrador, "admin-004@gymflow.test")
    token_admin = create_access_token({"sub": str(admin.id), "rol": "administrador"})
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token_admin)
    ).json()
    client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token_admin),
    )

    resp = client.post(
        f"/usuarios/{creado['id']}/membresias/renovar",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token_admin),
    )
    assert resp.status_code == 200


def test_historial_membresias(db):
    tipo = _crear_tipo(db)
    token = _token_empleado(db, permisos=("membership.renovar",))
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()
    client.post(
        f"/usuarios/{creado['id']}/membresias",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )
    client.post(
        f"/usuarios/{creado['id']}/membresias/renovar",
        json={"tipo_id": tipo.id, "monto": "50000"},
        headers=_headers(token),
    )

    resp = client.get(f"/usuarios/{creado['id']}/membresias", headers=_headers(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


# --- Restricción de qué rol puede crear/ascender cada actor (hallazgo posterior a HU-07) ---


def test_empleado_sin_permiso_no_puede_crear_administrador(db):
    token = _token_empleado(db)
    resp = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "administrador", "password": "clave123"},
        headers=_headers(token),
    )
    assert resp.status_code == 403


def test_empleado_sin_permiso_no_puede_crear_empleado(db):
    token = _token_empleado(db)
    resp = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "empleado", "password": "clave123"},
        headers=_headers(token),
    )
    assert resp.status_code == 403


def test_empleado_con_permiso_puede_crear_empleado_pero_no_administrador(db):
    token = _token_empleado(db, permisos=("members.asignar_rol_empleado",))

    crea_empleado = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "empleado", "password": "clave123"},
        headers=_headers(token),
    )
    assert crea_empleado.status_code == 201

    crea_admin = client.post(
        "/usuarios",
        json={"cedula": "2", "nombre": "Y", "rol": "administrador", "password": "clave123"},
        headers=_headers(token),
    )
    assert crea_admin.status_code == 403


def test_administrador_puede_crear_empleado_y_administrador(db):
    admin = _crear_staff(db, RolUsuario.administrador, "admin-roles@gymflow.test")
    token = create_access_token({"sub": str(admin.id), "rol": "administrador"})

    crea_empleado = client.post(
        "/usuarios",
        json={"cedula": "1", "nombre": "X", "rol": "empleado", "password": "clave123"},
        headers=_headers(token),
    )
    assert crea_empleado.status_code == 201

    crea_admin = client.post(
        "/usuarios",
        json={"cedula": "2", "nombre": "Y", "rol": "administrador", "password": "clave123"},
        headers=_headers(token),
    )
    assert crea_admin.status_code == 201


def test_empleado_sin_permiso_no_puede_ascender_miembro_a_empleado(db):
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    resp = client.put(
        f"/usuarios/{creado['id']}", json={"rol": "empleado"}, headers=_headers(token)
    )
    assert resp.status_code == 403


def test_empleado_con_permiso_puede_ascender_miembro_a_empleado_no_a_administrador(db):
    token = _token_empleado(db, permisos=("members.asignar_rol_empleado",))
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    asciende_empleado = client.put(
        f"/usuarios/{creado['id']}", json={"rol": "empleado"}, headers=_headers(token)
    )
    assert asciende_empleado.status_code == 200
    assert asciende_empleado.json()["rol"] == "empleado"

    asciende_admin = client.put(
        f"/usuarios/{creado['id']}", json={"rol": "administrador"}, headers=_headers(token)
    )
    assert asciende_admin.status_code == 403


def test_editar_sin_tocar_rol_no_dispara_la_restriccion(db):
    token = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    ).json()

    resp = client.put(
        f"/usuarios/{creado['id']}", json={"nombre": "Otro nombre"}, headers=_headers(token)
    )
    assert resp.status_code == 200


# --- members.gestionar_usuarios: CRUD básico de usuarios también gateado (hallazgo posterior) ---


def _token_empleado_sin_gestionar_usuarios(db) -> str:
    empleado = _crear_staff(db, RolUsuario.empleado, "empleado-sin-permiso@gymflow.test")
    return create_access_token({"sub": str(empleado.id), "rol": "empleado"})


def test_empleado_sin_gestionar_usuarios_no_puede_crear(db):
    token = _token_empleado_sin_gestionar_usuarios(db)
    resp = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    )
    assert resp.status_code == 403


def test_empleado_sin_gestionar_usuarios_no_puede_listar(db):
    token = _token_empleado_sin_gestionar_usuarios(db)
    resp = client.get("/usuarios", headers=_headers(token))
    assert resp.status_code == 403


def test_empleado_sin_gestionar_usuarios_no_puede_ver_uno(db):
    creador = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(creador)
    ).json()

    token = _token_empleado_sin_gestionar_usuarios(db)
    resp = client.get(f"/usuarios/{creado['id']}", headers=_headers(token))
    assert resp.status_code == 403


def test_empleado_sin_gestionar_usuarios_no_puede_editar(db):
    creador = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(creador)
    ).json()

    token = _token_empleado_sin_gestionar_usuarios(db)
    resp = client.put(
        f"/usuarios/{creado['id']}", json={"nombre": "Y"}, headers=_headers(token)
    )
    assert resp.status_code == 403


def test_empleado_sin_gestionar_usuarios_no_puede_eliminar(db):
    creador = _token_empleado(db)
    creado = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(creador)
    ).json()

    token = _token_empleado_sin_gestionar_usuarios(db)
    resp = client.delete(f"/usuarios/{creado['id']}", headers=_headers(token))
    assert resp.status_code == 403


def test_empleado_con_gestionar_usuarios_puede_crud_basico(db):
    token = _token_empleado(db)  # ya incluye members.gestionar_usuarios por defecto
    resp = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    )
    assert resp.status_code == 201


def test_administrador_no_necesita_gestionar_usuarios_explicito(db):
    admin = _crear_staff(db, RolUsuario.administrador, "admin-gestionar@gymflow.test")
    token = create_access_token({"sub": str(admin.id), "rol": "administrador"})
    resp = client.post(
        "/usuarios", json={"cedula": "1", "nombre": "X", "rol": "miembro"}, headers=_headers(token)
    )
    assert resp.status_code == 201
