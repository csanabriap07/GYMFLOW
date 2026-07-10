"""
Servicio de auth.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de auth.
Ningún otro módulo debe importar auth/repository.py directamente.

Para leer `usuarios` reutiliza members.service (auth no tiene repository
propio para esa tabla; solo lo tiene para `permisos`/`usuario_permisos`).
"""
from sqlalchemy.orm import Session

import members.service as members_service
from auth.repository import AuthRepository
from core.security import create_access_token, verify_password
from models import EstadoUsuario, Permiso, RolUsuario

_ROLES_BACKOFFICE = (RolUsuario.empleado, RolUsuario.administrador)


class CredencialesInvalidasError(Exception):
    """Cubre: email inexistente, password incorrecta, rol no es Empleado/
    Administrador, o estado inactivo. Nunca se distingue el motivo en la
    respuesta (spec.md: 'sin revelar si el usuario existe')."""


class PermisoInexistenteError(Exception):
    """El código de permiso pedido no está en el catálogo (004)."""


def login(email: str, password: str, db: Session) -> tuple[str, RolUsuario, set[str]]:
    user = members_service.get_user_by_email(email, db)

    credenciales_ok = (
        user is not None
        and user.password_hash is not None
        and user.rol in _ROLES_BACKOFFICE
        and user.estado == EstadoUsuario.activo
        and verify_password(password, user.password_hash)
    )
    if not credenciales_ok:
        raise CredencialesInvalidasError()

    token = create_access_token({"sub": str(user.id), "rol": user.rol.value})
    permisos = get_user_permissions(user.id, db)
    return token, user.rol, permisos


def get_user_permissions(usuario_id: int, db: Session) -> set[str]:
    return AuthRepository(db).get_permission_codes(usuario_id)


def list_permissions(usuario_id: int, db: Session) -> list[Permiso]:
    members_service.get_user(usuario_id, db)  # 404 limpio si no existe
    return AuthRepository(db).list_granted(usuario_id)


def list_permissions_catalog(db: Session) -> list[Permiso]:
    """Todo el catálogo (004): para que un administrador vea qué códigos
    existen antes de otorgar uno, en vez de escribirlo a ciegas."""
    return AuthRepository(db).list_catalog()


def grant_permission(usuario_id: int, codigo: str, db: Session) -> None:
    members_service.get_user(usuario_id, db)
    permiso = AuthRepository(db).get_permiso_by_codigo(codigo)
    if permiso is None:
        raise PermisoInexistenteError()
    AuthRepository(db).grant(usuario_id, permiso.id)
    db.commit()


def revoke_permission(usuario_id: int, codigo: str, db: Session) -> None:
    members_service.get_user(usuario_id, db)
    permiso = AuthRepository(db).get_permiso_by_codigo(codigo)
    if permiso is None:
        raise PermisoInexistenteError()
    AuthRepository(db).revoke(usuario_id, permiso.id)
    db.commit()
