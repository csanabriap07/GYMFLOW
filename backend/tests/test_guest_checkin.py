import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import hash_password, create_access_token
from models.user import User, RolUsuario, EstadoUsuario
from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType
from models.checkin import CheckIn, ResultadoCheckin
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from core.config import settings


class TestGuestCheckin:
    def _setup_titular(self, db: Session) -> tuple[User, Membership]:
        tipo = MembershipType(
            nombre="Mensual", precio_base=50, visitas_totales=30,
            cupo_invitados=4, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        user = User(
            cedula="11111111", nombre="Titular Test", email="titular@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("pass"),
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

        return user, membership

    def test_exito_invitado(self, db: Session, client: TestClient):
        titular, membership = self._setup_titular(db)

        tz = ZoneInfo(settings.timezone)
        ahora = datetime.now(tz)
        checkin = CheckIn(
            usuario_id=titular.id, fecha_hora=ahora, fecha=ahora.date(),
            resultado=ResultadoCheckin.exitoso,
        )
        db.add(checkin)
        db.flush()

        resp = client.post(
            "/checkin/guest",
            json={"cedula_invitado": "99999999", "cedula_titular": "11111111"},
            headers={"X-Device-Id": "guest-device"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["resultado"] == "exitoso"
        assert data["cupos_invitados"] == 2

    def test_titular_no_ingreso_primero(self, db: Session, client: TestClient):
        titular, membership = self._setup_titular(db)

        resp = client.post(
            "/checkin/guest",
            json={"cedula_invitado": "88888888", "cedula_titular": "11111111"},
            headers={"X-Device-Id": "guest-device-2"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "denegado"
        assert resp.json()["razon"] == "TITULAR_NO_INGRESO"

    def test_sin_cupos_invitados(self, db: Session, client: TestClient):
        titular, membership = self._setup_titular(db)
        membership.cupo_invitados_restantes = 0
        db.flush()

        tz = ZoneInfo(settings.timezone)
        ahora = datetime.now(tz)
        checkin = CheckIn(
            usuario_id=titular.id, fecha_hora=ahora, fecha=ahora.date(),
            resultado=ResultadoCheckin.exitoso,
        )
        db.add(checkin)
        db.flush()

        resp = client.post(
            "/checkin/guest",
            json={"cedula_invitado": "77777777", "cedula_titular": "11111111"},
            headers={"X-Device-Id": "guest-device-3"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "denegado"
        assert resp.json()["razon"] == "SIN_CUPOS_INVITADOS"

    def test_titular_sin_membresia(self, db: Session, client: TestClient):
        user = User(
            cedula="22222222", nombre="Sin Membresia", email="sinmembresia@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
        )
        db.add(user)
        db.flush()

        resp = client.post(
            "/checkin/guest",
            json={"cedula_invitado": "66666666", "cedula_titular": "22222222"},
            headers={"X-Device-Id": "guest-device-4"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "denegado"
        assert resp.json()["razon"] == "TITULAR_SIN_MEMBRESIA"

    def test_titular_no_encontrado(self, db: Session, client: TestClient):
        resp = client.post(
            "/checkin/guest",
            json={"cedula_invitado": "55555555", "cedula_titular": "00000000"},
            headers={"X-Device-Id": "guest-device-5"},
        )
        assert resp.status_code == 200
        assert resp.json()["resultado"] == "denegado"
        assert resp.json()["razon"] == "TITULAR_NO_ENCONTRADO"

    def test_cupo_se_descuenta_atomicamente(self, db: Session, client: TestClient):
        titular, membership = self._setup_titular(db)
        cupos_originales = membership.cupo_invitados_restantes

        tz = ZoneInfo(settings.timezone)
        ahora = datetime.now(tz)
        checkin = CheckIn(
            usuario_id=titular.id, fecha_hora=ahora, fecha=ahora.date(),
            resultado=ResultadoCheckin.exitoso,
        )
        db.add(checkin)
        db.flush()

        client.post(
            "/checkin/guest",
            json={"cedula_invitado": "44444444", "cedula_titular": "11111111"},
            headers={"X-Device-Id": "guest-device-6"},
        )

        db.refresh(membership)
        assert membership.cupo_invitados_restantes == cupos_originales - 1
