"""
Router de checkin (spec/features/001-checkin-membresia-activa). Validación de
entrada con Pydantic (checkin/schemas.py), nunca a mano aquí (AGENTS.md).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from checkin.schemas import CheckinRequest, CheckinResponse
from checkin.service import UsuarioNoEncontradoError, checkin_member
from core.database import get_db

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("", response_model=CheckinResponse)
def post_checkin(payload: CheckinRequest, db: Session = Depends(get_db)) -> CheckinResponse:
    try:
        resultado, mensaje, nombre, visitas_restantes = checkin_member(payload.cedula, db)
    except UsuarioNoEncontradoError:
        raise HTTPException(status_code=404, detail="Cédula no registrada")
    return CheckinResponse(
        resultado=resultado, mensaje=mensaje, nombre=nombre, visitas_restantes=visitas_restantes
    )
