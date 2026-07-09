"""
Repository de reports — lectura agregada sobre `checkins` para
spec/features/010-reportes-asistencia.

NOTA (discrepancia marcada en 010/spec.md): tech-stack.md describe este
repository como "lectura agregada sobre CheckIn", pero `CheckIn` es propiedad
de `checkin` y el límite duro prohíbe queries cruzadas saltándose el service
del módulo dueño. Resolución a implementar en 010: `reports.service` debe
pedir los datos vía `checkin.service` (no vía este repository contra la tabla
ajena) — o, si el equipo confirma una excepción explícita para reportes de
solo lectura, documentarla aquí antes de implementarla. No asumido en este
scaffold.
"""
from sqlalchemy.orm import Session


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db
