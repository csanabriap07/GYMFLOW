import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import hash_password, create_access_token
from core.qr import encode_qr, decode_qr
from models.user import User, RolUsuario, EstadoUsuario


def _admin_token(db: Session) -> str:
    admin = User(
        cedula="00000000", nombre="Admin", email="admin@test.com",
        rol=RolUsuario.administrador, estado=EstadoUsuario.activo,
        password_hash=hash_password("pass"),
    )
    db.add(admin)
    db.flush()
    return create_access_token(data={"sub": str(admin.id), "rol": "administrador"})


class TestSearch:
    def test_busqueda_cedula_exacta(self, db: Session, client: TestClient):
        token = _admin_token(db)
        user = User(
            cedula="12345678", nombre="Juan Perez", email="juan@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        resp = client.get("/usuarios/search?q=12345678", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["cedula"] == "12345678"

    def test_busqueda_nombre_parcial(self, db: Session, client: TestClient):
        token = _admin_token(db)
        for i in range(3):
            user = User(
                cedula=f"1111111{i}", nombre=f"Maria {i}", email=f"maria{i}@test.com",
                rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            )
            db.add(user)
        db.flush()

        resp = client.get("/usuarios/search?q=Maria", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_busqueda_sin_resultados(self, db: Session, client: TestClient):
        token = _admin_token(db)
        resp = client.get("/usuarios/search?q=ZZZZZ", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert len(resp.json()) == 0


class TestQR:
    def test_encode_decode_qr(self):
        cedula = "12345678"
        encoded = encode_qr(cedula)
        decoded = decode_qr(encoded)
        assert decoded is not None
        assert decoded["cedula"] == cedula

    def test_decode_qr_invalido(self):
        assert decode_qr("invalid") is None

    def test_checkin_qr_valido(self, db: Session, client: TestClient):
        from models.membership import Membership, EstadoMembresia
        from models.membership_type import MembershipType
        from datetime import datetime
        from zoneinfo import ZoneInfo
        from core.config import settings

        tipo = MembershipType(
            nombre="Mensual", precio_base=50, visitas_totales=30,
            cupo_invitados=4, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        user = User(
            cedula="87654321", nombre="QR User", email="qr@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        membership = Membership(
            miembro_id=user.id, tipo_id=tipo.id,
            visitas_restantes=10, cupo_invitados_restantes=2,
            fecha_inicio="2026-07-01", fecha_vencimiento="2026-08-01",
            estado=EstadoMembresia.activa,
        )
        db.add(membership)
        db.flush()

        payload = encode_qr("87654321")
        resp = client.post(
            f"/checkin/qr?qr_payload={payload}",
            headers={"X-Device-Id": "qr-device"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "exitoso"

    def test_checkin_qr_invalido(self, db: Session, client: TestClient):
        resp = client.post(
            "/checkin/qr?qr_payload=invalid",
            headers={"X-Device-Id": "qr-device-2"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "denegado"
        assert resp.json()["razon"] == "QR_INVALIDO"
