from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class MembershipTypeCreate(BaseModel):
    nombre: str
    precio_base: Decimal
    visitas_totales: int
    cupo_invitados: int = 0
    duracion_dias: int
    activo: bool = True


class MembershipTypeUpdate(BaseModel):
    nombre: str | None = None
    precio_base: Decimal | None = None
    visitas_totales: int | None = None
    cupo_invitados: int | None = None
    duracion_dias: int | None = None
    activo: bool | None = None


class MembershipTypeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    precio_base: Decimal
    visitas_totales: int
    cupo_invitados: int
    duracion_dias: int
    activo: bool


class MembershipSummaryOut(BaseModel):
    tipo: str
    estado: str
    visitas_restantes: int
    cupo_invitados_restantes: int
    fecha_inicio: str
    fecha_vencimiento: str
    proximo_pago: str
