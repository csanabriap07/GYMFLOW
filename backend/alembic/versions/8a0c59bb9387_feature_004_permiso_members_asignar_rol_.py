"""HU-07: permiso members.asignar_rol_empleado

Revision ID: 8a0c59bb9387
Revises: 1d22a2198fbe
Create Date: 2026-07-10 16:31:54.656544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a0c59bb9387'
down_revision = '1d22a2198fbe'
branch_labels = None
depends_on = None


permisos_table = sa.table(
    "permisos",
    sa.column("codigo", sa.String),
    sa.column("descripcion", sa.String),
)

_CATALOGO_NUEVO = [
    {
        "codigo": "members.asignar_rol_empleado",
        "descripcion": (
            "Crear un usuario con rol empleado, o ascender un usuario existente a "
            "empleado (POST /usuarios, PUT /usuarios/{id}). Ascender/crear con rol "
            "administrador sigue reservado exclusivamente al rol administrador, "
            "ningún permiso individual lo habilita."
        ),
    },
]


def upgrade() -> None:
    op.bulk_insert(permisos_table, _CATALOGO_NUEVO)


def downgrade() -> None:
    op.execute("DELETE FROM permisos WHERE codigo = 'members.asignar_rol_empleado'")
