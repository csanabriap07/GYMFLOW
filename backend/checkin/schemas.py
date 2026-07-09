"""
Schemas Pydantic de checkin (entrada/salida de API). Se agregan al implementar
spec/features/001, 002, 005, 006/. Toda validación de entrada vive aquí, nunca a
mano en el router (AGENTS.md).
"""
from pydantic import BaseModel

from checkin.service import CheckinResultado


class CheckinRequest(BaseModel):
    cedula: str


class CheckinResponse(BaseModel):
    resultado: CheckinResultado
    mensaje: str
    nombre: str | None = None
    visitas_restantes: int | None = None
