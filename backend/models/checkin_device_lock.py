"""
Tabla `checkin_device_locks` — dueño: checkin.
Control de bloqueo de dispositivo tras intentos fallidos (RN-03).
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Index

from core.database import Base


class CheckinDeviceLock(Base):
    __tablename__ = "checkin_device_locks"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), nullable=False, index=True)
    intentos_fallidos = Column(Integer, nullable=False, default=0)
    ventana_inicio = Column(DateTime(timezone=True), nullable=False)
    bloqueado_hasta = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_device_lock_unico", "device_id", unique=True),
    )
