"""
Servicio de members.

Regla de módulos del proyecto (no negociable): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de members.
Ningún otro módulo debe importar members/repository.py directamente.
"""
from decimal import Decimal

from sqlalchemy.orm import Session

import membership.service as membership_service
from core.security import hash_password
from members.repository import MembersRepository
from models import EstadoUsuario, Membership, RolUsuario, User


class UsuarioNoEncontradoError(Exception):
    """El `user_id` pedido no existe (HU-07)."""


class CedulaYaRegistradaError(Exception):
    """Ya existe un usuario con esa cédula (HU-07) — se valida antes del
    INSERT/UPDATE para no dejar reventar un IntegrityError sin capturar."""


class EmailYaRegistradoError(Exception):
    """Ya existe un usuario con ese email (HU-07), misma razón que arriba."""


class RolNoPermitidoError(Exception):
    """El actor no puede crear/ascender un usuario al rol pedido (HU-07, RF-09): ver
    `puede_asignar_rol`."""


PERMISO_ASIGNAR_ROL_EMPLEADO = "members.asignar_rol_empleado"


def puede_asignar_rol(actor_rol: RolUsuario, actor_permisos: set[str], rol_objetivo: RolUsuario) -> bool:
    """Determina si el actor puede crear o ascender un usuario a ``rol_objetivo``.

    - ``administrador``: reservado exclusivamente a un actor administrador,
      ningún permiso individual lo habilita.
    - ``empleado``: administrador, o un empleado con el permiso individual
      ``members.asignar_rol_empleado``.
    - ``miembro``/``invitado``: cualquier staff autenticado, sin restricción
      extra.

    Args:
        actor_rol: Rol del usuario que hace la petición.
        actor_permisos: Códigos de permiso individuales del actor.
        rol_objetivo: Rol que se quiere asignar/ascender.

    Returns:
        ``True`` si el actor puede asignar ese rol.
    """
    if rol_objetivo == RolUsuario.administrador:
        return actor_rol == RolUsuario.administrador
    if rol_objetivo == RolUsuario.empleado:
        return actor_rol == RolUsuario.administrador or PERMISO_ASIGNAR_ROL_EMPLEADO in actor_permisos
    return True


def get_user_by_cedula(cedula: str, db: Session) -> User | None:
    return MembersRepository(db).get_by_cedula(cedula)


def get_user_by_email(email: str, db: Session) -> User | None:
    return MembersRepository(db).get_by_email(email)


def get_user(user_id: int, db: Session) -> User:
    """Busca un usuario por ID.

    Raises:
        UsuarioNoEncontradoError: si ``user_id`` no existe.
    """
    user = MembersRepository(db).get_by_id(user_id)
    if user is None:
        raise UsuarioNoEncontradoError()
    return user


def list_users(db: Session) -> list[User]:
    return MembersRepository(db).list_all()


def get_users_by_ids(user_ids: list[int], db: Session) -> dict[int, User]:
    """Resuelve varios usuarios en lote (evita N+1 al enriquecer el reporte
    de asistencias, HU-09). Punto de entrada del módulo dueño de ``usuarios``
    para que ``reports`` no consulte esa tabla directamente.

    Args:
        user_ids: IDs a resolver.
        db: Sesión de base de datos activa.

    Returns:
        Diccionario ``{user_id: User}``; los IDs sin usuario no aparecen.
    """
    return {u.id: u for u in MembersRepository(db).list_by_ids(user_ids)}


def _validar_unicidad(
    db: Session, cedula: str, email: str | None, excluir_id: int | None = None
) -> None:
    repo = MembersRepository(db)
    existente_cedula = repo.get_by_cedula(cedula)
    if existente_cedula is not None and existente_cedula.id != excluir_id:
        raise CedulaYaRegistradaError()
    if email is not None:
        existente_email = repo.get_by_email(email)
        if existente_email is not None and existente_email.id != excluir_id:
            raise EmailYaRegistradoError()


def create_user(
    cedula: str,
    nombre: str,
    email: str | None,
    rol: RolUsuario,
    estado: EstadoUsuario,
    password: str | None,
    db: Session,
) -> User:
    """Crea un usuario.

    Args:
        cedula: Cédula única del usuario.
        nombre: Nombre completo.
        email: Correo único, o ``None``.
        rol: Rol asignado.
        estado: Estado inicial.
        password: Contraseña en texto plano a hashear, o ``None`` para
            crear el usuario sin contraseña (activación posterior).
        db: Sesión de base de datos activa.

    Raises:
        CedulaYaRegistradaError: si ``cedula`` ya está registrada.
        EmailYaRegistradoError: si ``email`` ya está registrado.
    """
    _validar_unicidad(db, cedula, email)
    user = User(
        cedula=cedula,
        nombre=nombre,
        email=email,
        rol=rol,
        estado=estado,
        password_hash=hash_password(password) if password else None,
    )
    user = MembersRepository(db).create(user)
    db.commit()
    return user


def update_user(user_id: int, db: Session, **fields) -> User:
    """Actualiza los campos dados de un usuario.

    Args:
        user_id: ID del usuario a actualizar.
        db: Sesión de base de datos activa.
        **fields: Campos a modificar (p. ej. ``cedula``, ``email``,
            ``password``); ``password`` se hashea antes de guardarse.

    Raises:
        UsuarioNoEncontradoError: si ``user_id`` no existe.
        CedulaYaRegistradaError: si la nueva ``cedula`` ya está en uso por
            otro usuario.
        EmailYaRegistradoError: si el nuevo ``email`` ya está en uso por
            otro usuario.
    """
    user = get_user(user_id, db)
    cedula = fields.get("cedula", user.cedula)
    email = fields.get("email", user.email)
    _validar_unicidad(db, cedula, email, excluir_id=user_id)

    password = fields.pop("password", None)
    if password:
        fields["password_hash"] = hash_password(password)

    user = MembersRepository(db).update(user, **fields)
    db.commit()
    return user


def anonymize_user(user_id: int, db: Session) -> User:
    """Borra la PII del usuario de forma irreversible (RN-07), preservando la
    fila (y su ``id``) para no romper la FK de ``CheckIn.usuario_id`` — el
    histórico de check-ins del usuario se conserva.

    Args:
        user_id: ID del usuario a anonimizar.
        db: Sesión de base de datos activa.

    Raises:
        UsuarioNoEncontradoError: si ``user_id`` no existe.
    """
    user = get_user(user_id, db)
    user = MembersRepository(db).update(
        user,
        cedula=None,
        nombre=None,
        email=None,
        password_hash=None,
        estado=EstadoUsuario.inactivo,
    )
    db.commit()
    return user


def assign_membership(
    user_id: int, tipo_id: int, monto: Decimal, nota: str | None, db: Session
) -> Membership:
    get_user(user_id, db)  # 404 limpio si el usuario no existe
    membership = membership_service.create_membership(user_id, tipo_id, monto, nota, db)
    db.commit()
    return membership


def renew_membership(
    user_id: int, tipo_id: int, monto: Decimal, nota: str | None, db: Session
) -> Membership:
    get_user(user_id, db)
    membership = membership_service.renew_membership(user_id, tipo_id, monto, nota, db)
    db.commit()
    return membership


def get_membership_history(user_id: int, db: Session) -> list[Membership]:
    get_user(user_id, db)
    return membership_service.list_membership_history(user_id, db)
