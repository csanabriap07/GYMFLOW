import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import hash_password, create_access_token
from models.user import User, RolUsuario, EstadoUsuario
from models.membership_type import MembershipType


def _admin_token(db: Session) -> tuple[str, User]:
    admin = User(
        cedula="00000000", nombre="Admin", email="admin@test.com",
        rol=RolUsuario.administrador, estado=EstadoUsuario.activo,
        password_hash=hash_password("pass"),
    )
    db.add(admin)
    db.flush()
    token = create_access_token(data={"sub": str(admin.id), "rol": "administrador"})
    return token, admin


class TestUserCRUD:
    def test_create_user(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        resp = client.post(
            "/usuarios",
            json={"cedula": "11111111", "nombre": "Nuevo", "email": "nuevo@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["cedula"] == "11111111"
        assert data["nombre"] == "Nuevo"

    def test_create_user_with_password(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        resp = client.post(
            "/usuarios",
            json={
                "cedula": "22222222",
                "nombre": "Staff",
                "email": "staff@test.com",
                "rol": "empleado",
                "password": "pass123",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_create_user_email_duplicado(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        client.post(
            "/usuarios",
            json={"cedula": "33333333", "nombre": "A", "email": "dup@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.post(
            "/usuarios",
            json={"cedula": "44444444", "nombre": "B", "email": "dup@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    def test_list_users(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        resp = client.get("/usuarios", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_user(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        create_resp = client.post(
            "/usuarios",
            json={"cedula": "55555555", "nombre": "Get", "email": "get@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        user_id = create_resp.json()["id"]
        resp = client.get(f"/usuarios/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["id"] == user_id

    def test_update_user(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        create_resp = client.post(
            "/usuarios",
            json={"cedula": "66666666", "nombre": "Old", "email": "old@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        user_id = create_resp.json()["id"]
        resp = client.put(
            f"/usuarios/{user_id}",
            json={"nombre": "New"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "New"

    def test_delete_user_anonymizes(self, db: Session, client: TestClient):
        token, _ = _admin_token(db)
        create_resp = client.post(
            "/usuarios",
            json={"cedula": "77777777", "nombre": "Delete", "email": "del@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        user_id = create_resp.json()["id"]
        resp = client.delete(f"/usuarios/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

        from members.repository import MembersRepository

        repo = MembersRepository(db)
        user = repo.get_by_id(user_id)
        assert user.cedula is None
        assert user.nombre is None
        assert user.email is None
        assert user.estado == "inactivo"


class TestAssignMembership:
    def test_assign_membership(self, db: Session, client: TestClient):
        tipo = MembershipType(
            nombre="Mensual", precio_base=50, visitas_totales=30,
            cupo_invitados=4, duracion_dias=30, activo=True,
        )
        db.add(tipo)
        db.flush()

        token, _ = _admin_token(db)
        create_resp = client.post(
            "/usuarios",
            json={"cedula": "88888888", "nombre": "Socio", "email": "socio@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        user_id = create_resp.json()["id"]

        resp = client.post(
            f"/usuarios/{user_id}/membresia",
            params={"tipo_id": tipo.id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["visitas_restantes"] == 30
        assert data["cupo_invitados_restantes"] == 4
        assert data["estado"] == "activa"


class TestRBACMembers:
    def test_401_sin_token(self, client: TestClient):
        assert client.get("/usuarios").status_code == 401

    def test_403_rol_miembro(self, db: Session, client: TestClient):
        user = User(
            cedula="99999999", nombre="Miembro", email="m@test.com",
            rol=RolUsuario.miembro, estado=EstadoUsuario.activo,
            password_hash=hash_password("pass"),
        )
        db.add(user)
        db.flush()
        token = create_access_token(data={"sub": str(user.id), "rol": "miembro"})
        assert client.get("/usuarios", headers={"Authorization": f"Bearer {token}"}).status_code == 403

    def test_empleado_puede_listar(self, db: Session, client: TestClient):
        user = User(
            cedula="00000001", nombre="Emp", email="emp@test.com",
            rol=RolUsuario.empleado, estado=EstadoUsuario.activo,
            password_hash=hash_password("pass"),
        )
        db.add(user)
        db.flush()
        token = create_access_token(data={"sub": str(user.id), "rol": "empleado"})
        assert client.get("/usuarios", headers={"Authorization": f"Bearer {token}"}).status_code == 200

    def test_empleado_no_puede_crear(self, db: Session, client: TestClient):
        user = User(
            cedula="00000002", nombre="Emp2", email="emp2@test.com",
            rol=RolUsuario.empleado, estado=EstadoUsuario.activo,
            password_hash=hash_password("pass"),
        )
        db.add(user)
        db.flush()
        token = create_access_token(data={"sub": str(user.id), "rol": "empleado"})
        resp = client.post(
            "/usuarios",
            json={"cedula": "12345000", "nombre": "X", "email": "x@test.com"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
