"""
Tabla `checkins` — dueño: checkin (ver tech-stack.md). Registro inmutable.
"""
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func

from core.database import Base


class ResultadoCheckin(str, enum.Enum):
    exitoso = "exitoso"
    denegado = "denegado"


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    fecha_hora = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resultado = Column(Enum(ResultadoCheckin), nullable=False)
    # Distingue al menos: MEMBRESIA_VENCIDA, SIN_VISITAS, YA_INGRESO_HOY,
    # DISPOSITIVO_BLOQUEADO (ver 002-acceso-denegado).
    razon_denegacion = Column(String(50), nullable=True)
    # Solo se llena en check-in de invitado (ver 006-checkin-invitado).
    titular_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    # NOTA (001/002): el índice único parcial (usuario_id, fecha) para check-ins
    # exitosos (anti doble check-in, RN-02) se agrega en la migración de la
    # feature 001, no en este scaffold.
