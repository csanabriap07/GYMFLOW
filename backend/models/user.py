"""
Tabla `usuarios` — dueño: members (ver tech-stack.md).
"""
import enum

from sqlalchemy import Column, Integer, String, Enum, DateTime, func

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

    id = Column(Integer, primary_key=True, index=True)
    # nullable=True: RN-07 anonimiza (borra PII) preservando la fila para el
    # histórico de CheckIn (FK usuario_id). Ver duda abierta en 004-gestion-usuarios.
    cedula = Column(String(20), unique=True, index=True, nullable=True)
    nombre = Column(String(150), nullable=True)
    email = Column(String(150), unique=True, nullable=True)
    rol = Column(Enum(RolUsuario), nullable=False, default=RolUsuario.miembro)
    estado = Column(Enum(EstadoUsuario), nullable=False, default=EstadoUsuario.activo)
    # Solo Empleado/Administrador tienen credenciales (HU-10, RN-12). Nunca texto plano.
    password_hash = Column(String(255), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    # NOTA (duda abierta 005-cortesia-primer-dia): la marca de "cortesía usada" /
    # rol Prospecto NO se agrega en este scaffold. Se define junto con el equipo
    # al implementar esa feature, vía migración Alembic dedicada.
