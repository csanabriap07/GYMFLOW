from datetime import date

from sqlalchemy.orm import Session

from models.membership import Membership, EstadoMembresia
from models.membership_type import MembershipType


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_user_id(self, user_id: int, hoy: date) -> Membership | None:
        return (
            self.db.query(Membership)
            .filter(
                Membership.miembro_id == user_id,
                Membership.estado == EstadoMembresia.activa,
                Membership.fecha_vencimiento >= hoy,
                Membership.visitas_restantes > 0,
            )
            .order_by(Membership.fecha_vencimiento.asc())
            .first()
        )

    def get_by_id(self, membership_id: int) -> Membership | None:
        return self.db.query(Membership).filter(Membership.id == membership_id).first()

    def consume_visit(self, membership_id: int, db: Session) -> Membership:
        membership = (
            db.query(Membership)
            .filter(Membership.id == membership_id)
            .with_for_update()
            .first()
        )
        if membership is None:
            raise ValueError("MEMBRESIA_NO_ENCONTRADA")
        if membership.visitas_restantes <= 0:
            raise ValueError("SIN_VISITAS")
        membership.visitas_restantes -= 1
        return membership

    def consume_guest_slot(self, membership_id: int, db: Session) -> Membership:
        membership = (
            db.query(Membership)
            .filter(Membership.id == membership_id)
            .with_for_update()
            .first()
        )
        if membership is None:
            raise ValueError("MEMBRESIA_NO_ENCONTRADA")
        if membership.cupo_invitados_restantes <= 0:
            raise ValueError("SIN_CUPOS_INVITADOS")
        membership.cupo_invitados_restantes -= 1
        return membership

    def create(self, membership: Membership) -> Membership:
        self.db.add(membership)
        self.db.flush()
        return membership


class MembershipTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tipo_id: int) -> MembershipType | None:
        return self.db.query(MembershipType).filter(MembershipType.id == tipo_id).first()

    def list_all(self) -> list[MembershipType]:
        return self.db.query(MembershipType).order_by(MembershipType.id.asc()).all()

    def list_active(self) -> list[MembershipType]:
        return self.db.query(MembershipType).filter(MembershipType.activo == True).all()

    def create(self, tipo: MembershipType) -> MembershipType:
        self.db.add(tipo)
        self.db.flush()
        return tipo

    def update(self, tipo: MembershipType) -> MembershipType:
        self.db.flush()
        return tipo

    def count_active_memberships(self, tipo_id: int) -> int:
        from datetime import date
        return (
            self.db.query(Membership)
            .filter(
                Membership.tipo_id == tipo_id,
                Membership.estado == EstadoMembresia.activa,
                Membership.fecha_vencimiento >= date.today(),
            )
            .count()
        )
