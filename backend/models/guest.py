"""
Tabla `invitados` — dueño pendiente de confirmar (duda abierta en
006-checkin-invitado). Se propone `members`, a confirmar con el equipo.
"""
from sqlalchemy import Column, Integer, String, ForeignKey

from core.database import Base


class Guest(Base):
    __tablename__ = "invitados"

    id = Column(Integer, primary_key=True, index=True)
    cedula = Column(String(20), nullable=True, index=True)
    nombre = Column(String(150), nullable=True)
    titular_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
