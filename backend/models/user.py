"""
Tabla `usuarios` — dueño: el módulo members.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class RolUsuario(str, enum.Enum):
    invitado = "invitado"
    miembro = "miembro"
    empleado = "empleado"
    administrador = "administrador"


class EstadoUsuario(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    # nullable=True: RN-07 anonimiza (borra PII) preservando la fila para el
    # histórico de CheckIn (FK usuario_id). Duda abierta de HU-07.
    cedula: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str | None] = mapped_column(String(150))
    email: Mapped[str | None] = mapped_column(String(150), unique=True)
    rol: Mapped[RolUsuario] = mapped_column(default=RolUsuario.miembro)
    estado: Mapped[EstadoUsuario] = mapped_column(default=EstadoUsuario.activo)
    # Solo Empleado/Administrador tienen credenciales (HU-10, RN-12). Nunca texto plano.
    password_hash: Mapped[str | None] = mapped_column(String(255))
    creado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # NOTA (duda abierta de HU-04 — Cortesía de primer día): la marca de "cortesía usada" /
    # rol Prospecto NO se agrega en este scaffold. Se define junto con el equipo
    # al implementar esa feature, vía migración Alembic dedicada.
