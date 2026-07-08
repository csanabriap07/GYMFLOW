from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import require_role
from models.user import User
from reports.schemas import AttendanceRow
from reports.service import generate_report, export_csv, export_xlsx

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/attendance", response_model=list[AttendanceRow])
def attendance_report(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("administrador")),
):
    return generate_report(fecha_inicio, fecha_fin, db)


@router.get("/attendance/export")
def attendance_export(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    format: str = Query("csv", pattern="^(csv|xlsx)$"),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("administrador")),
):
    rows = generate_report(fecha_inicio, fecha_fin, db)

    if format == "xlsx":
        content = export_xlsx(rows)
        return StreamingResponse(
            iter([content]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=asistencia.xlsx"},
        )

    content = export_csv(rows)
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=asistencia.csv"},
    )
