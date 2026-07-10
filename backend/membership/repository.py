"""
Repository de membership — único punto de acceso a `membresias` y
`tipos_membresia` (AGENTS.md). Métodos concretos se agregan al implementar
spec/features/001, 004, 007, 009.
"""
from datetime import date

from sqlalchemy.orm import Session

from models import Membership, MembershipType, EstadoMembresia


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_user(self, user_id: int, hoy: date) -> Membership | None:
        """La fila "vigente" es la que está en ventana de fechas
        (fecha_inicio <= hoy), no solo la que tiene estado=activa: una
        renovación anticipada (004) puede dejar dos filas en estado=activa
        simultáneamente (la vieja, todavía vigente, y la nueva, con
        fecha_inicio en el futuro) — sin este filtro y el order_by,
        `.first()` elegiría una de las dos de forma no determinística."""
        return (
            self.db.query(Membership)
            .filter(
                Membership.miembro_id == user_id,
                Membership.estado == EstadoMembresia.activa,
                Membership.fecha_inicio <= hoy,
            )
            .order_by(Membership.fecha_inicio.desc(), Membership.id.desc())
            .first()
        )

    def get_latest_by_user(self, user_id: int) -> Membership | None:
        """La última fila creada para el usuario, sea cual sea su estado o
        fecha — usada por 004 para encontrar "la anterior" al renovar.
        Desempata por `id` cuando dos filas comparten `fecha_inicio` (ej. una
        renovación el mismo día que la anterior ya había vencido)."""
        return (
            self.db.query(Membership)
            .filter(Membership.miembro_id == user_id)
            .order_by(Membership.fecha_inicio.desc(), Membership.id.desc())
            .first()
        )

    def list_by_user(self, user_id: int) -> list[Membership]:
        return (
            self.db.query(Membership)
            .filter(Membership.miembro_id == user_id)
            .order_by(Membership.fecha_inicio.desc(), Membership.id.desc())
            .all()
        )

    def create(self, membership: Membership) -> Membership:
        self.db.add(membership)
        self.db.flush()
        return membership

    def get_for_update(self, membership_id: int) -> Membership:
        """SELECT ... FOR UPDATE — serializa descuentos concurrentes (plan.md de 001)."""
        return (
            self.db.query(Membership)
            .filter(Membership.id == membership_id)
            .with_for_update()
            .one()
        )


class MembershipTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tipo_id: int) -> MembershipType | None:
        return self.db.query(MembershipType).filter(MembershipType.id == tipo_id).first()

    def list_active(self) -> list[MembershipType]:
        """Solo los tipos `activo=true` — no tiene sentido ofrecer para
        asignar/renovar (004) un tipo que ya fue desactivado (009)."""
        return (
            self.db.query(MembershipType)
            .filter(MembershipType.activo.is_(True))
            .order_by(MembershipType.nombre)
            .all()
        )
