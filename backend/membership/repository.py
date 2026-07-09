"""
Repository de membership — único punto de acceso a `membresias` y
`tipos_membresia` (AGENTS.md). Métodos concretos se agregan al implementar
spec/features/001, 007, 009.
"""
from sqlalchemy.orm import Session


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db


class MembershipTypeRepository:
    def __init__(self, db: Session):
        self.db = db
