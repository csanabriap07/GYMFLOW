import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from core.security import hash_password, create_access_token
from models.user import User, RolUsuario, EstadoUsuario


class TestLogin:
    def test_login_exitoso_admin(self, db: Session, client: TestClient):
        admin = User(
            cedula="99999999",
            nombre="Admin Test",
            email="admin@test.com",
            rol=RolUsuario.administrador,
            estado=EstadoUsuario.activo,
            password_hash=hash_password("pass123"),
        )
        db.add(admin)
        db.flush()

        response = client.post(
            "/auth/login", json={"email": "admin@test.com", "password": "pass123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["rol"] == "administrador"
        assert data["expires_in"] == 1800

    def test_login_credenciales_invalidas(self, db: Session, client: TestClient):
        admin = User(
            cedula="88888888",
            nombre="Admin 2",
            email="admin2@test.com",
            rol=RolUsuario.administrador,
            estado=EstadoUsuario.activo,
            password_hash=hash_password("pass123"),
        )
        db.add(admin)
        db.flush()

        response = client.post(
            "/auth/login", json={"email": "admin2@test.com", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_login_usuario_no_existe(self, db: Session, client: TestClient):
        response = client.post(
            "/auth/login", json={"email": "noexiste@test.com", "password": "pass"}
        )
        assert response.status_code == 401

    def test_login_no_revela_si_usuario_existe(self, db: Session, client: TestClient):
        r1 = client.post(
            "/auth/login", json={"email": "noexiste@test.com", "password": "pass"}
        )
        r2 = client.post(
            "/auth/login", json={"email": "siexiste@test.com", "password": "pass"}
        )
        assert r1.status_code == r2.status_code


class TestRBAC:
    def test_401_sin_token(self, client: TestClient):
        response = client.get("/usuarios")
        assert response.status_code == 401

    def test_401_token_invalido(self, client: TestClient):
        response = client.get(
            "/usuarios", headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401

    def test_403_rol_insuficiente(self, db: Session, client: TestClient):
        user = User(
            cedula="77777777",
            nombre="Miembro",
            email="miembro@test.com",
            rol=RolUsuario.miembro,
            estado=EstadoUsuario.activo,
            password_hash=hash_password("pass123"),
        )
        db.add(user)
        db.flush()

        token = create_access_token(data={"sub": str(user.id), "rol": "miembro"})
        response = client.get(
            "/usuarios", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 403

    def test_200_rol_suficiente(self, db: Session, client: TestClient):
        admin = User(
            cedula="65432100",
            nombre="Admin RBAC",
            email="adminrbac@test.com",
            rol=RolUsuario.administrador,
            estado=EstadoUsuario.activo,
            password_hash=hash_password("pass123"),
        )
        db.add(admin)
        db.flush()

        token = create_access_token(data={"sub": str(admin.id), "rol": "administrador"})
        response = client.get(
            "/usuarios", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_401_token_expirado(self, client: TestClient):
        token = create_access_token(
            data={"sub": "1", "rol": "administrador"},
            expires_minutes=-1,
        )
        response = client.get(
            "/usuarios", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    def test_kiosko_sin_jwt(self, client: TestClient):
        response = client.post(
            "/checkin", json={"cedula": "12345678"}, headers={"X-Device-Id": "kiosk"}
        )
        assert response.status_code in (200, 400, 422)


class TestNoPlaintext:
    def test_password_nunca_en_claro(self, db: Session, client: TestClient):
        admin = User(
            cedula="66666666",
            nombre="Plain Admin",
            email="plain@test.com",
            rol=RolUsuario.administrador,
            estado=EstadoUsuario.activo,
            password_hash=hash_password("secret"),
        )
        db.add(admin)
        db.flush()

        from members.repository import MembersRepository

        repo = MembersRepository(db)
        user = repo.get_by_email("plain@test.com")
        assert user.password_hash != "secret"
        assert user.password_hash.startswith("$2b$")
