from pydantic import BaseModel, EmailStr

from models.user import RolUsuario, EstadoUsuario


class UserCreate(BaseModel):
    cedula: str
    nombre: str
    email: EmailStr
    rol: RolUsuario = RolUsuario.miembro
    estado: EstadoUsuario = EstadoUsuario.activo
    password: str | None = None


class UserUpdate(BaseModel):
    cedula: str | None = None
    nombre: str | None = None
    email: EmailStr | None = None
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

    model_config = {"from_attributes": True}
