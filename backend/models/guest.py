"""
Tabla `invitados` — dueño pendiente de confirmar (duda abierta de HU-05 —
Check-in de invitado). Se propone `members`, a confirmar con el equipo.
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class Guest(Base):
    __tablename__ = "invitados"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cedula: Mapped[str | None] = mapped_column(String(20), index=True)
    nombre: Mapped[str | None] = mapped_column(String(150))
    titular_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
