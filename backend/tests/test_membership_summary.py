import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User, RolUsuario, EstadoUsuario
from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType


class TestMembershipSummary:
    def test_resumen_miembro_activo(self, db: Session, client: TestClient):
        tipo = MembershipType(
            nombre="Mensual", precio_base=50, visitas_totales=30,
            cupo_invitados=4, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        user = User(
            cedula="11111111", nombre="Test", email="test@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        membership = Membership(
            miembro_id=user.id, tipo_id=tipo.id,
            visitas_restantes=20, cupo_invitados_restantes=3,
            fecha_inicio="2026-07-01", fecha_vencimiento="2026-08-01",
            estado=EstadoMembresia.activa,
        )
        db.add(membership)
        db.flush()

        resp = client.get("/membresias/summary?cedula=11111111")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "Mensual"
        assert data["estado"] == "activa"
        assert data["visitas_restantes"] == 20
        assert data["cupo_invitados_restantes"] == 3
        assert data["proximo_pago"] == "2026-08-01"

    def test_resumen_miembro_sin_membresia(self, db: Session, client: TestClient):
        user = User(
            cedula="22222222", nombre="Sin Plan", email="sinplan@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        resp = client.get("/membresias/summary?cedula=22222222")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tipo"] == "Sin membresía"
        assert data["estado"] == "vencida"
        assert data["visitas_restantes"] == 0

    def test_resumen_usuario_no_encontrado(self, db: Session, client: TestClient):
        resp = client.get("/membresias/summary?cedula=00000000")
        assert resp.status_code == 404

    def test_resumen_no_descuenta_visitas(self, db: Session, client: TestClient):
        tipo = MembershipType(
            nombre="Mensual", precio_base=50, visitas_totales=30,
            cupo_invitados=4, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        user = User(
            cedula="33333333", nombre="NoDescuenta", email="nodescuenta@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        membership = Membership(
            miembro_id=user.id, tipo_id=tipo.id,
            visitas_restantes=20, cupo_invitados_restantes=3,
            fecha_inicio="2026-07-01", fecha_vencimiento="2026-08-01",
            estado=EstadoMembresia.activa,
        )
        db.add(membership)
        db.flush()

        client.get("/membresias/summary?cedula=33333333")
        client.get("/membresias/summary?cedula=33333333")

        db.refresh(membership)
        assert membership.visitas_restantes == 20
        assert membership.cupo_invitados_restantes == 3
