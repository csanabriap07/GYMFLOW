"""
Router de auth.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import auth.service as auth_service
from auth.dependencies import require_role
from auth.schemas import LoginRequest, LoginResponse, PermisoGrantRequest, PermisoOut
from auth.service import CredencialesInvalidasError, PermisoInexistenteError
from auth.service import login as login_service
from core.database import get_db
from members.service import UsuarioNoEncontradoError
from models import RolUsuario

router = APIRouter(prefix="/auth", tags=["auth"])

_ADMIN = Depends(require_role(RolUsuario.administrador))


@router.post("/login", response_model=LoginResponse)
def post_login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    try:
        token, rol, permisos = login_service(payload.email, payload.password, db)
    except CredencialesInvalidasError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas")
    return LoginResponse(access_token=token, rol=rol, permisos=sorted(permisos))


@router.get("/permisos", response_model=list[PermisoOut])
def get_catalogo_permisos(db: Session = Depends(get_db), _admin=_ADMIN) -> list[PermisoOut]:
    return [PermisoOut.model_validate(p) for p in auth_service.list_permissions_catalog(db)]


@router.get("/usuarios/{user_id}/permisos", response_model=list[PermisoOut])
def get_permisos_usuario(
    user_id: int, db: Session = Depends(get_db), _admin=_ADMIN
) -> list[PermisoOut]:
    try:
        permisos = auth_service.list_permissions(user_id, db)
    except UsuarioNoEncontradoError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return [PermisoOut.model_validate(p) for p in permisos]


@router.post("/usuarios/{user_id}/permisos", status_code=status.HTTP_204_NO_CONTENT)
def post_otorgar_permiso(
    user_id: int, payload: PermisoGrantRequest, db: Session = Depends(get_db), _admin=_ADMIN
) -> None:
    try:
        auth_service.grant_permission(user_id, payload.codigo, db)
    except UsuarioNoEncontradoError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    except PermisoInexistenteError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Código de permiso no existe")


@router.delete("/usuarios/{user_id}/permisos/{codigo}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quitar_permiso(
    user_id: int, codigo: str, db: Session = Depends(get_db), _admin=_ADMIN
) -> None:
    try:
        auth_service.revoke_permission(user_id, codigo, db)
    except UsuarioNoEncontradoError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    except PermisoInexistenteError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Código de permiso no existe")
