"""
Tabla `membresias` — dueño: el módulo membership.
"""
import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class EstadoMembresia(str, enum.Enum):
    activa = "activa"
    vencida = "vencida"


class Membership(Base):
    __tablename__ = "membresias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    miembro_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    tipo_id: Mapped[int] = mapped_column(ForeignKey("tipos_membresia.id"))
    visitas_restantes: Mapped[int]
    cupo_invitados_restantes: Mapped[int]
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_vencimiento: Mapped[date] = mapped_column(Date)
    estado: Mapped[EstadoMembresia] = mapped_column(default=EstadoMembresia.activa)
    # Trazabilidad del pago en ventanilla (004-gestion-usuarios) — GymFlow no
    # procesa pagos, esto es solo la anotación de lo cobrado, no una integración.
    monto: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    nota: Mapped[str | None] = mapped_column(String(255))
