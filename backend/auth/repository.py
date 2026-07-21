"""
Repository de auth — único punto de acceso a las tablas `permisos` y
`usuario_permisos` (HU-10 — Autenticación segura) y `refresh_tokens`
(Portal del Miembro, RF-02/RF-04). `auth` sigue sin repository
para `usuarios`: esa tabla es del módulo members.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Permiso, RefreshToken, usuario_permisos


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_permission_codes(self, usuario_id: int) -> set[str]:
        query = (
            select(Permiso.codigo)
            .join(usuario_permisos, usuario_permisos.c.permiso_id == Permiso.id)
            .where(usuario_permisos.c.usuario_id == usuario_id)
        )
        return set(self.db.scalars(query).all())

    def get_permiso_by_codigo(self, codigo: str) -> Permiso | None:
        return self.db.query(Permiso).filter(Permiso.codigo == codigo).first()

    def list_catalog(self) -> list[Permiso]:
        """Todo el catálogo de permisos (no solo los otorgados a un usuario) —
        para que un administrador vea qué códigos existen antes de otorgar
        uno (HU-07)."""
        return self.db.query(Permiso).order_by(Permiso.codigo).all()

    def list_granted(self, usuario_id: int) -> list[Permiso]:
        query = (
            select(Permiso)
            .join(usuario_permisos, usuario_permisos.c.permiso_id == Permiso.id)
            .where(usuario_permisos.c.usuario_id == usuario_id)
            .order_by(Permiso.codigo)
        )
        return list(self.db.scalars(query).all())

    def grant(self, usuario_id: int, permiso_id: int) -> None:
        ya_otorgado = self.db.execute(
            select(usuario_permisos).where(
                usuario_permisos.c.usuario_id == usuario_id,
                usuario_permisos.c.permiso_id == permiso_id,
            )
        ).first()
        if ya_otorgado is None:
            self.db.execute(
                usuario_permisos.insert().values(usuario_id=usuario_id, permiso_id=permiso_id)
            )

    def revoke(self, usuario_id: int, permiso_id: int) -> None:
        self.db.execute(
            usuario_permisos.delete().where(
                usuario_permisos.c.usuario_id == usuario_id,
                usuario_permisos.c.permiso_id == permiso_id,
            )
        )


class RefreshTokenRepository:
    """Tabla `refresh_tokens` (Portal del Miembro): sesión larga del Miembro. Solo se
    persiste el hash del token; la generación/hash vive en auth/service."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, token: RefreshToken) -> RefreshToken:
        self.db.add(token)
        self.db.flush()
        return token

    def get_vigente_by_hash(self, token_hash: str, ahora: datetime) -> RefreshToken | None:
        query = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revocado_en.is_(None),
            RefreshToken.expira_en >= ahora,
        )
        return self.db.scalars(query).first()

    def revoke(self, token: RefreshToken, ahora: datetime) -> None:
        token.revocado_en = ahora
