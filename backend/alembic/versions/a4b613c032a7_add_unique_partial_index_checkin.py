"""add fecha column and unique partial index on checkins

Revision ID: a4b613c032a7
Revises: faae8fa060f4
Create Date: 2026-07-08 05:15:29.391159

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4b613c032a7'
down_revision = 'faae8fa060f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("checkins", sa.Column("fecha", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")))
    op.alter_column("checkins", "fecha", server_default=None)
    op.create_index(
        "ix_checkin_unico_dia",
        "checkins",
        ["usuario_id", "fecha"],
        unique=True,
        postgresql_where=sa.text("resultado = 'exitoso'"),
    )


def downgrade() -> None:
    op.drop_index("ix_checkin_unico_dia", table_name="checkins", postgresql_where=sa.text("resultado = 'exitoso'"))
    op.drop_column("checkins", "fecha")
