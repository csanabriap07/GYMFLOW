"""
Tabla `tipos_membresia` — dueño: membership (ver tech-stack.md).
Plantilla configurable de planes; no se elimina/desactiva con membresías activas
vinculadas (RN-05); editarla no altera contratos vigentes (RN-06, ver 009).
"""
from decimal import Decimal

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class MembershipType(Base):
    __tablename__ = "tipos_membresia"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    precio_base: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    visitas_totales: Mapped[int]
    cupo_invitados: Mapped[int] = mapped_column(default=0)
    duracion_dias: Mapped[int]
    activo: Mapped[bool] = mapped_column(default=True)
