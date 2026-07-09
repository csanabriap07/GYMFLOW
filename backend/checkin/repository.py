"""
Repository de checkin — único punto de acceso a la tabla `checkins` (AGENTS.md).
Métodos concretos se agregan al implementar spec/features/001, 002, 005, 006.
"""
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.config import settings
from models import CheckIn


class CheckinRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_successful_checkin_today(self, user_id: int, hoy: date) -> bool:
        """RN-02 (Filtro 1): filtra explícitamente por día calendario (zona
        horaria del gimnasio) además de `is_active` — un `is_active=true` de
        un día anterior no cuenta (ver spec.md de 001)."""
        dia_gimnasio = func.date(func.timezone(settings.timezone, CheckIn.fecha_hora))
        return (
            self.db.query(CheckIn)
            .filter(
                CheckIn.usuario_id == user_id,
                CheckIn.is_active.is_(True),
                dia_gimnasio == hoy,
            )
            .first()
            is not None
        )

    def insert(self, checkin: CheckIn) -> CheckIn:
        self.db.add(checkin)
        self.db.flush()
        return checkin
