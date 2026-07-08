import csv
import io
from datetime import date

from sqlalchemy.orm import Session

from checkin.service import get_attendance
from reports.schemas import AttendanceRow


def generate_report(fecha_inicio: date, fecha_fin: date, db: Session) -> list[AttendanceRow]:
    rows = get_attendance(fecha_inicio, fecha_fin, db)
    return [AttendanceRow(**r) for r in rows]


def export_csv(rows: list[AttendanceRow]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Usuario", "Cédula", "Fecha/Hora", "Resultado", "Razón"])
    for r in rows:
        writer.writerow([r.id, r.usuario_nombre, r.usuario_cedula, r.fecha_hora, r.resultado, r.razon or ""])
    return output.getvalue()


def export_xlsx(rows: list[AttendanceRow]) -> bytes:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Asistencia"
    ws.append(["ID", "Usuario", "Cédula", "Fecha/Hora", "Resultado", "Razón"])
    for r in rows:
        ws.append([r.id, r.usuario_nombre, r.usuario_cedula, r.fecha_hora, r.resultado, r.razon or ""])

    output = io.BytesIO()
    wb.save(output)
    return output.getvalue()
