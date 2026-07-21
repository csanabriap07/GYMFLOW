"""
Schemas Pydantic de checkin (entrada/salida de API) — HU-01, HU-02, HU-04 y
HU-05. Toda validación de entrada vive aquí, nunca a mano en el router
(convención del proyecto).
"""
import enum
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel


class CheckinResultado(str, enum.Enum):
    exitoso = "exitoso"
    denegado = "denegado"


class RazonDenegacion(str, enum.Enum):
    """HU-02 — sin `YA_INGRESO_HOY`: un reingreso el mismo día es
    Exitoso (HU-01, RN-02), no una razón de denegación."""

    membresia_vencida = "MEMBRESIA_VENCIDA"
    sin_visitas = "SIN_VISITAS"
    cedula_no_encontrada = "CEDULA_NO_ENCONTRADA"
    dispositivo_bloqueado = "DISPOSITIVO_BLOQUEADO"


class CheckinRequest(BaseModel):
    cedula: str


class CheckinResponse(BaseModel):
    resultado: CheckinResultado
    mensaje: str
    nombre: str | None = None
    visitas_restantes: int | None = None
    razon: RazonDenegacion | None = None


class AttendancePointOut(BaseModel):
    fecha: date
    asistencias: int


class AttendanceConsistencyOut(BaseModel):
    periodo: Literal["semana", "mes"]
    total: int
    puntos: list[AttendancePointOut]


class DispositivoBloqueadoResponse(BaseModel):
    mensaje: str
    bloqueado_hasta: datetime


class DispositivoBloqueadoInfo(BaseModel):
    """Para que Staff sepa qué `device_id` pasarle al endpoint de desbloqueo
    manual — sin esto no hay forma de saber cuál dispositivo es cuál."""

    device_id: str
    intentos_fallidos: int
    bloqueado_hasta: datetime

    model_config = {"from_attributes": True}
