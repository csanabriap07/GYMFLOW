from sqlalchemy.orm import Session

from models.user import User


class MembersRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_cedula(self, cedula: str) -> User | None:
        return self.db.query(User).filter(User.cedula == cedula).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        return user

    def list_all(self) -> list[User]:
        return self.db.query(User).order_by(User.id).all()

    def update(self, user: User) -> User:
        self.db.flush()
        return user

    def anonymize(self, user: User) -> User:
        user.cedula = None
        user.nombre = None
        user.email = None
        user.estado = "inactivo"
        self.db.flush()
        return user

    def search_by_name_or_cedula(self, query: str) -> list[User]:
        pattern = f"%{query}%"
        return (
            self.db.query(User)
            .filter(
                (User.nombre.ilike(pattern)) | (User.cedula.ilike(pattern))
            )
            .order_by(User.nombre)
            .all()
        )
