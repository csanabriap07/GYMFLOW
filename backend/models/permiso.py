"""
Tablas `permisos` y `usuario_permisos` — dueño: el módulo auth (HU-10, RF-09).
Permisos individuales por usuario, independientes del rol. `administrador`
tiene implícitamente todos los permisos (ver auth/dependencies.py), no
necesita filas en `usuario_permisos`.
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base

usuario_permisos = Table(
    "usuario_permisos",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("permiso_id", Integer, ForeignKey("permisos.id"), primary_key=True),
)


class Permiso(Base):
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))
