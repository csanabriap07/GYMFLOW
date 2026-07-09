"""
Tabla `membresias` — dueño: membership (ver tech-stack.md).
"""
import enum

from sqlalchemy import Column, Integer, ForeignKey, Enum, Date

from core.database import Base


class EstadoMembresia(str, enum.Enum):
    activa = "activa"
    vencida = "vencida"


class Membership(Base):
    __tablename__ = "membresias"

    id = Column(Integer, primary_key=True, index=True)
    miembro_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    tipo_id = Column(Integer, ForeignKey("tipos_membresia.id"), nullable=False)
    visitas_restantes = Column(Integer, nullable=False)
    cupo_invitados_restantes = Column(Integer, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estado = Column(Enum(EstadoMembresia), nullable=False, default=EstadoMembresia.activa)
