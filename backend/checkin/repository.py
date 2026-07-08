from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from core.config import settings
from models.checkin import CheckIn, ResultadoCheckin
from models.checkin_device_lock import CheckinDeviceLock


class CheckinRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_successful_today(self, user_id: int, hoy: datetime) -> bool:
        return (
            self.db.query(CheckIn)
            .filter(
                CheckIn.usuario_id == user_id,
                CheckIn.fecha == hoy,
                CheckIn.resultado == ResultadoCheckin.exitoso,
            )
            .first()
            is not None
        )

    def get_last_successful_member_checkin(self, user_id: int, device_id: str):
        ahora = datetime.now(ZoneInfo(settings.timezone))
        ventana_inicio = ahora - timedelta(minutes=settings.ventana_invitado_min)
        return (
            self.db.query(CheckIn)
            .filter(
                CheckIn.usuario_id == user_id,
                CheckIn.resultado == ResultadoCheckin.exitoso,
                CheckIn.fecha_hora >= ventana_inicio,
            )
            .order_by(CheckIn.fecha_hora.desc())
            .first()
        )

    def insert(self, checkin: CheckIn) -> CheckIn:
        self.db.add(checkin)
        self.db.flush()
        return checkin

    def register_denied(self, device_id: str, ahora: datetime) -> None:
        tz = ZoneInfo(settings.timezone)
        ventana_inicio = ahora - timedelta(minutes=5)
        lock = (
            self.db.query(CheckinDeviceLock)
            .filter(CheckinDeviceLock.device_id == device_id)
            .first()
        )
        if lock is None:
            lock = CheckinDeviceLock(
                device_id=device_id,
                intentos_fallidos=1,
                ventana_inicio=ahora,
                bloqueado_hasta=None,
            )
            self.db.add(lock)
        else:
            if lock.ventana_inicio < ventana_inicio:
                lock.intentos_fallidos = 1
                lock.ventana_inicio = ahora
                lock.bloqueado_hasta = None
            else:
                lock.intentos_fallidos += 1
                if lock.intentos_fallidos >= 3:
                    lock.bloqueado_hasta = ahora + timedelta(minutes=20)
        self.db.flush()

    def reset_attempts(self, device_id: str) -> None:
        lock = (
            self.db.query(CheckinDeviceLock)
            .filter(CheckinDeviceLock.device_id == device_id)
            .first()
        )
        if lock is not None:
            lock.intentos_fallidos = 0
            lock.bloqueado_hasta = None
            self.db.flush()

    def is_locked(self, device_id: str, ahora: datetime) -> bool:
        lock = (
            self.db.query(CheckinDeviceLock)
            .filter(CheckinDeviceLock.device_id == device_id)
            .first()
        )
        if lock is None or lock.bloqueado_hasta is None:
            return False
        return ahora < lock.bloqueado_hasta
