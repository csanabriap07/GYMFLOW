import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User, RolUsuario, EstadoUsuario
from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType
from models.checkin import CheckIn, ResultadoCheckin
from core.security import hash_password, create_access_token


@pytest.fixture
def admin_token(db: Session) -> str:
    admin = User(
        cedula="99999999",
        nombre="Admin",
        email="admin@test.com",
        rol=RolUsuario.administrador,
        estado=EstadoUsuario.activo,
        password_hash=hash_password("Admin123"),
    )
    db.add(admin)
    db.flush()
    return create_access_token(data={"sub": str(admin.id), "rol": "administrador"})


@pytest.fixture
def report_data(db: Session):
    user = User(
        cedula="12345678",
        nombre="Juan Perez",
        email="juan@test.com",
        rol=RolUsuario.miembro,
        estado=EstadoUsuario.activo,
        password_hash=hash_password("test"),
    )
    db.add(user)
    db.flush()

    tipo = MembershipType(
        nombre="Mensual", precio_base=50.00, visitas_totales=10,
        cupo_invitados=2, duracion_dias=30, activo=True,
    )
    db.add(tipo)
    db.flush()

    membership = Membership(
        miembro_id=user.id, tipo_id=tipo.id,
        visitas_restantes=5, cupo_invitados_restantes=2,
        fecha_inicio=date(2026, 1, 1), fecha_vencimiento=date(2099, 12, 31),
        estado=EstadoMembresia.activa,
    )
    db.add(membership)
    db.flush()

    ci = CheckIn(
        usuario_id=user.id,
        fecha_hora=datetime(2026, 7, 1, 10, 30),
        fecha=date(2026, 7, 1),
        resultado=ResultadoCheckin.exitoso,
    )
    db.add(ci)
    db.commit()

    return {"user": user, "tipo": tipo, "membership": membership, "checkin": ci}


class TestReports:
    def test_attendance_report(self, client: TestClient, db: Session, admin_token: str, report_data):
        resp = client.get(
            "/reports/attendance",
            params={"fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-31"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1
        assert data[0]["usuario_nombre"] == "Juan Perez"
        assert data[0]["resultado"] == "exitoso"

    def test_attendance_report_empty_range(self, client: TestClient, db: Session, admin_token: str):
        resp = client.get(
            "/reports/attendance",
            params={"fecha_inicio": "2020-01-01", "fecha_fin": "2020-01-31"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json() == []

    def test_export_csv(self, client: TestClient, db: Session, admin_token: str, report_data):
        resp = client.get(
            "/reports/attendance/export",
            params={"fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-31", "format": "csv"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert "Juan Perez" in resp.text

    def test_export_xlsx(self, client: TestClient, db: Session, admin_token: str, report_data):
        resp = client.get(
            "/reports/attendance/export",
            params={"fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-31", "format": "xlsx"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert "spreadsheetml" in resp.headers["content-type"]

    def test_requires_admin_role(self, client: TestClient, db: Session):
        user = User(
            cedula="33333333", nombre="Miembro", email="m@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("test"),
        )
        db.add(user)
        db.flush()
        token = create_access_token(data={"sub": str(user.id), "rol": "miembro"})

        resp = client.get(
            "/reports/attendance",
            params={"fecha_inicio": "2026-07-01", "fecha_fin": "2026-07-31"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
