"""
Repository de reports — lectura agregada sobre `checkins` para
HU-09 — Reportes de asistencia.

NOTA: aunque el diseño inicial describía este repository como "lectura
agregada sobre CheckIn", `CheckIn` es propiedad del módulo checkin y la regla
de módulos prohíbe queries cruzadas saltándose el service del módulo dueño.
Resolución adoptada en HU-09: `reports.service` pide los datos vía
`checkin.service` (no vía este repository contra la tabla ajena).
"""
from sqlalchemy.orm import Session


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db
