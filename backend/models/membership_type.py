"""
Tabla `tipos_membresia` — dueño: membership (ver tech-stack.md).
Plantilla configurable de planes; no se elimina/desactiva con membresías activas
vinculadas (RN-05); editarla no altera contratos vigentes (RN-06, ver 009).
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean

from core.database import Base


class MembershipType(Base):
    __tablename__ = "tipos_membresia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio_base = Column(Numeric(10, 2), nullable=False)
    visitas_totales = Column(Integer, nullable=False)
    cupo_invitados = Column(Integer, nullable=False, default=0)
    duracion_dias = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
