import enum
from pydantic import BaseModel


class RazonDenegacion(str, enum.Enum):
    MEMBRESIA_VENCIDA = "MEMBRESIA_VENCIDA"
    SIN_VISITAS = "SIN_VISITAS"
    YA_INGRESO_HOY = "YA_INGRESO_HOY"
    DISPOSITIVO_BLOQUEADO = "DISPOSITIVO_BLOQUEADO"
    USUARIO_NO_ENCONTRADO = "USUARIO_NO_ENCONTRADO"
    CORTESIA_YA_UTILIZADA = "CORTESIA_YA_UTILIZADA"


class CheckinRequest(BaseModel):
    cedula: str


class GuestCheckinRequest(BaseModel):
    cedula_invitado: str
    cedula_titular: str


class CheckinResponse(BaseModel):
    resultado: str
    mensaje: str
    razon: str | None = None
    nombre: str | None = None
    visitas_restantes: int | None = None
    cupos_invitados: int | None = None
    membresia: dict | None = None
    bloqueado_hasta: str | None = None
    cortesia: bool | None = None
