"""
Schemas Pydantic de auth (entrada/salida de API). Toda validación de entrada
vive aquí, nunca a mano en el router (convención del proyecto).
"""
from pydantic import BaseModel, Field

from models import RolUsuario


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: RolUsuario
    permisos: list[str]


class PortalLoginRequest(BaseModel):
    """Portal del Miembro: login del Miembro (RF-02/RF-04)."""

    email: str
    password: str


class PortalSessionResponse(BaseModel):
    """Portal del Miembro: respuesta de login/refresh. El refresh token NO va
    aquí — viaja solo en la cookie httpOnly. `nombre` alimenta el saludo
    del Dashboard."""

    access_token: str
    token_type: str = "bearer"
    nombre: str | None


class PortalActivateRequest(BaseModel):
    """Portal del Miembro: activación de cuenta creada por el staff.
    Contraseña no vacía — mismo criterio que el alta de staff
    (HU-07 no fija un mínimo de longitud; no se inventa uno aquí)."""

    cedula: str
    email: str
    password: str = Field(min_length=1)


class PermisoGrantRequest(BaseModel):
    """HU-07 — Gestión de usuarios: otorgar un permiso individual a un usuario."""

    codigo: str


class PermisoOut(BaseModel):
    codigo: str
    descripcion: str | None

    model_config = {"from_attributes": True}
