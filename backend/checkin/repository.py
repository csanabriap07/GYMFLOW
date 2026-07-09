"""
Repository de checkin — único punto de acceso a la tabla `checkins` (AGENTS.md).
Métodos concretos se agregan al implementar spec/features/001, 002, 005, 006.
"""
from sqlalchemy.orm import Session


class CheckinRepository:
    def __init__(self, db: Session):
        self.db = db
