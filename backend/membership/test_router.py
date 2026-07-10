"""
Tests HTTP de membership/router.py — lectura mínima de tipos activos para 004.
"""
from decimal import Decimal

from fastapi.testclient import TestClient

from auth.conftest import _crear_staff
from core.security import create_access_token
from main import app
from models import MembershipType, RolUsuario

client = TestClient(app)


def _crear_tipo(db, **overrides) -> MembershipType:
    defaults = dict(
        nombre="Mensual", precio_base=Decimal("50000"), visitas_totales=30,
        cupo_invitados=1, duracion_dias=30, activo=True,
    )
    defaults.update(overrides)
    tipo = MembershipType(**defaults)
    db.add(tipo)
    db.commit()
    return tipo


def test_get_tipos_sin_token_401(db):
    resp = client.get("/membresias/tipos")
    assert resp.status_code == 401


def test_get_tipos_lista_solo_activos(db):
    _crear_tipo(db, nombre="Activo")
    _crear_tipo(db, nombre="Inactivo", activo=False)
    empleado = _crear_staff(db, RolUsuario.empleado, "empleado-tipos@gymflow.test")
    token = create_access_token({"sub": str(empleado.id), "rol": "empleado"})

    resp = client.get("/membresias/tipos", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    assert [t["nombre"] for t in resp.json()] == ["Activo"]
