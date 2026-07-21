"""
Schemas Pydantic de members (entrada/salida de API, HU-07 — Gestión de
usuarios). Toda validación de entrada vive aquí, nunca a mano en el router
(convención del proyecto).
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Self

from pydantic import BaseModel, model_validator

from models import EstadoUsuario, RolUsuario

_ROLES_CON_CREDENCIALES = (RolUsuario.empleado, RolUsuario.administrador)


class UserCreate(BaseModel):
    cedula: str
    nombre: str
    email: str | None = None
    rol: RolUsuario
    estado: EstadoUsuario = EstadoUsuario.activo
    # Obligatorio solo para Empleado/Administrador (HU-10, RN-12); un
    # Miembro/Invitado no tiene login propio en este scaffold.
    password: str | None = None

    @model_validator(mode="after")
    def password_obligatoria_para_staff(self) -> Self:
        if self.rol in _ROLES_CON_CREDENCIALES and not self.password:
            raise ValueError("password es obligatoria para rol empleado/administrador")
        return self


class UserUpdate(BaseModel):
    cedula: str | None = None
    nombre: str | None = None
    email: str | None = None
    rol: RolUsuario | None = None
    estado: EstadoUsuario | None = None
    password: str | None = None


class UserOut(BaseModel):
    id: int
    cedula: str | None
    nombre: str | None
    email: str | None
    rol: RolUsuario
    estado: EstadoUsuario
    creado_en: datetime | None

    model_config = {"from_attributes": True}


class MembershipActionRequest(BaseModel):
    """Body compartido por asignar (primera vez) y renovar (HU-07)."""

    tipo_id: int
    monto: Decimal
    nota: str | None = None


class MembershipHistoryItem(BaseModel):
    id: int
    tipo_id: int
    monto: Decimal
    nota: str | None
    fecha_inicio: date
    fecha_vencimiento: date
    visitas_restantes: int
    cupo_invitados_restantes: int
    # Calculado a partir de las fechas al momento de leer, no del campo
    # `estado` guardado — evita el caso de doble membresía activa (HU-07).
    vigente: bool

    model_config = {"from_attributes": True}
