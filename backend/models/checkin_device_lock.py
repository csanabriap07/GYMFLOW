"""
Tabla `checkin_device_locks` — dueño: checkin (spec/features/002-acceso-denegado,
RN-03). Contador de intentos fallidos por dispositivo en tabla (no en memoria),
para ser correcto con múltiples workers de uvicorn en Docker.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class CheckinDeviceLock(Base):
    __tablename__ = "checkin_device_locks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    intentos_fallidos: Mapped[int] = mapped_column(default=0)
    # Inicio de la ventana deslizante de ≤5 min (RN-03); None si no hay fallos activos.
    ventana_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # None si no está bloqueado; si tiene fecha futura, el kiosko rechaza check-ins.
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
