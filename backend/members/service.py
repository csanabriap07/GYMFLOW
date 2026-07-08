from sqlalchemy.orm import Session

from core.security import hash_password
from members.repository import MembersRepository
from models.user import User
import membership.service as membership_service


def get_user_by_cedula(cedula: str, db: Session):
    repo = MembersRepository(db)
    user = repo.get_by_cedula(cedula)
    if user is None:
        raise ValueError("USUARIO_NO_ENCONTRADO")
    return user


def get_user_by_email(email: str, db: Session):
    repo = MembersRepository(db)
    return repo.get_by_email(email)


def create_user(data: dict, db: Session) -> User:
    repo = MembersRepository(db)
    if data.get("email") and repo.get_by_email(data["email"]):
        raise ValueError("EMAIL_DUPLICADO")
    if data.get("cedula") and repo.get_by_cedula(data["cedula"]):
        raise ValueError("CEDULA_DUPLICADA")

    user = User(
        cedula=data["cedula"],
        nombre=data["nombre"],
        email=data["email"],
        rol=data.get("rol", "miembro"),
        estado=data.get("estado", "activo"),
    )
    if data.get("password"):
        user.password_hash = hash_password(data["password"])
    return repo.create(user)


def get_user(user_id: int, db: Session) -> User:
    repo = MembersRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("USUARIO_NO_ENCONTRADO")
    return user


def list_users(db: Session) -> list[User]:
    repo = MembersRepository(db)
    return repo.list_all()


def update_user(user_id: int, data: dict, db: Session) -> User:
    repo = MembersRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("USUARIO_NO_ENCONTRADO")

    if "email" in data and data["email"] is not None:
        existing = repo.get_by_email(data["email"])
        if existing and existing.id != user_id:
            raise ValueError("EMAIL_DUPLICADO")
    if "cedula" in data and data["cedula"] is not None:
        existing = repo.get_by_cedula(data["cedula"])
        if existing and existing.id != user_id:
            raise ValueError("CEDULA_DUPLICADA")

    for field in ("cedula", "nombre", "email", "rol", "estado"):
        if field in data and data[field] is not None:
            setattr(user, field, data[field])
    if "password" in data and data["password"]:
        user.password_hash = hash_password(data["password"])
    return repo.update(user)


def anonymize_user(user_id: int, db: Session) -> User:
    repo = MembersRepository(db)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("USUARIO_NO_ENCONTRADO")
    return repo.anonymize(user)


def assign_membership(user_id: int, tipo_id: int, db: Session):
    get_user(user_id, db)
    return membership_service.create_membership(user_id, tipo_id, db)


def has_used_courtesy(cedula: str, db: Session) -> bool:
    repo = MembersRepository(db)
    user = repo.get_by_cedula(cedula)
    return user is not None and user.cortesia_usada


def create_prospect(cedula: str, db: Session) -> User:
    repo = MembersRepository(db)
    user = User(
        cedula=cedula,
        nombre=None,
        email=None,
        rol="invitado",
        estado="activo",
        cortesia_usada=True,
    )
    return repo.create(user)


def get_guest_by_cedula(cedula: str, db: Session):
    repo = MembersRepository(db)
    return repo.get_by_cedula(cedula)


def create_guest(cedula: str, titular_id: int, db: Session) -> User:
    repo = MembersRepository(db)
    user = User(
        cedula=cedula,
        nombre=None,
        email=None,
        rol="invitado",
        estado="activo",
    )
    return repo.create(user)


def search_users(query: str, db: Session) -> list[User]:
    repo = MembersRepository(db)
    if query.isdigit():
        user = repo.get_by_cedula(query)
        return [user] if user else []
    return repo.search_by_name_or_cedula(query)
