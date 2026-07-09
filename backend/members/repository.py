"""
Repository de members — único punto de acceso a la tabla `usuarios` (AGENTS.md).
Métodos concretos se agregan al implementar spec/features/001, 004, 005, 006.
"""
from sqlalchemy.orm import Session


class MembersRepository:
    def __init__(self, db: Session):
        self.db = db
