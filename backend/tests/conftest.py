import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.config import settings
from core.database import Base, get_db
from models.user import User, RolUsuario, EstadoUsuario
from models.membership_type import MembershipType
from models.membership import Membership, EstadoMembresia

TEST_DATABASE_URL = settings.database_url.replace("5432/gymflow", "5432/gymflow_test")


@pytest.fixture(scope="session")
def engine():
    e = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=e)
    yield e
    Base.metadata.drop_all(bind=e)


@pytest.fixture
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session):
    from main import app

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(db: Session):
    tipo = MembershipType(
        nombre="Test Mensual",
        precio_base=49.99,
        visitas_totales=30,
        cupo_invitados=4,
        duracion_dias=30,
        activo=True,
    )
    db.add(tipo)
    db.flush()

    user = User(
        cedula="12345678",
        nombre="Juan Perez",
        email="juan@test.com",
        rol=RolUsuario.miembro,
        estado=EstadoUsuario.activo,
    )
    db.add(user)
    db.flush()

    membership = Membership(
        miembro_id=user.id,
        tipo_id=tipo.id,
        visitas_restantes=5,
        cupo_invitados_restantes=2,
        fecha_inicio="2026-07-01",
        fecha_vencimiento="2026-08-01",
        estado=EstadoMembresia.activa,
    )
    db.add(membership)
    db.flush()

    return {"tipo": tipo, "user": user, "membership": membership}
