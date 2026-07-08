from pydantic import BaseModel
from datetime import date


class ReportFilters(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class AttendanceRow(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: str
    usuario_cedula: str
    fecha_hora: str
    resultado: str
    razon: str | None = None
