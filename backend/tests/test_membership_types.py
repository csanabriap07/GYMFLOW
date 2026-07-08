import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User, RolUsuario, EstadoUsuario
from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType
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


class TestMembershipTypeCRUD:
    def test_list_tipos(self, client: TestClient, db: Session, admin_token: str):
        resp = client.get("/membresias/tipos", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_tipo(self, client: TestClient, db: Session, admin_token: str):
        data = {
            "nombre": "Mensual",
            "precio_base": "50.00",
            "visitas_totales": 12,
            "cupo_invitados": 2,
            "duracion_dias": 30,
            "activo": True,
        }
        resp = client.post("/membresias/tipos", json=data, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["nombre"] == "Mensual"
        assert body["visitas_totales"] == 12
        assert body["activo"] is True

    def test_get_tipo_by_id(self, client: TestClient, db: Session, admin_token: str):
        tipo = MembershipType(
            nombre="Semanal", precio_base=20.00, visitas_totales=5,
            cupo_invitados=0, duracion_dias=7, activo=True,
        )
        db.add(tipo)
        db.commit()

        resp = client.get(f"/membresias/tipos/{tipo.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Semanal"

    def test_update_tipo(self, client: TestClient, db: Session, admin_token: str):
        tipo = MembershipType(
            nombre="Trimestral", precio_base=120.00, visitas_totales=30,
            cupo_invitados=4, duracion_dias=90, activo=True,
        )
        db.add(tipo)
        db.commit()

        resp = client.put(
            f"/membresias/tipos/{tipo.id}",
            json={"precio_base": "150.00", "visitas_totales": 40},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["precio_base"] == "150.00"
        assert resp.json()["visitas_totales"] == 40

    def test_delete_tipo_no_memberships(self, client: TestClient, db: Session, admin_token: str):
        tipo = MembershipType(
            nombre="Temp", precio_base=10.00, visitas_totales=1,
            cupo_invitados=0, duracion_dias=1, activo=True,
        )
        db.add(tipo)
        db.commit()

        resp = client.delete(f"/membresias/tipos/{tipo.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 204

    def test_delete_tipo_with_active_memberships_rejected(self, client: TestClient, db: Session, admin_token: str):
        from models.user import User, RolUsuario, EstadoUsuario

        user = User(
            cedula="11111111", nombre="Socio", email="socio@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("test"),
        )
        db.add(user)
        db.flush()

        tipo = MembershipType(
            nombre="Activo", precio_base=50.00, visitas_totales=10,
            cupo_invitados=2, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        membership = Membership(
            miembro_id=user.id, tipo_id=tipo.id,
            visitas_restantes=5, cupo_invitados_restantes=1,
            fecha_inicio="2026-01-01", fecha_vencimiento="2099-12-31",
            estado=EstadoMembresia.activa,
        )
        db.add(membership)
        db.commit()

        resp = client.delete(f"/membresias/tipos/{tipo.id}", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 409

    def test_deactivate_tipo_with_active_memberships_rejected(self, client: TestClient, db: Session, admin_token: str):
        from models.user import User, RolUsuario, EstadoUsuario

        user = User(
            cedula="22222222", nombre="Socio2", email="socio2@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("test"),
        )
        db.add(user)
        db.flush()

        tipo = MembershipType(
            nombre="Vitalicia", precio_base=999.00, visitas_totales=999,
            cupo_invitados=99, duracion_dias=365, activo=True,
        )
        db.add(tipo)
        db.flush()

        membership = Membership(
            miembro_id=user.id, tipo_id=tipo.id,
            visitas_restantes=100, cupo_invitados_restantes=10,
            fecha_inicio="2026-01-01", fecha_vencimiento="2099-12-31",
            estado=EstadoMembresia.activa,
        )
        db.add(membership)
        db.commit()

        resp = client.patch(f"/membresias/tipos/{tipo.id}/desactivar", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 409

    def test_requires_admin_role(self, client: TestClient, db: Session):
        user = User(
            cedula="33333333", nombre="Miembro", email="m@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("test"),
        )
        db.add(user)
        db.flush()
        token = create_access_token(data={"sub": str(user.id), "rol": "miembro"})

        resp = client.get("/membresias/tipos", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
