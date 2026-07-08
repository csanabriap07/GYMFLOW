from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from checkin.schemas import CheckinRequest, GuestCheckinRequest, CheckinResponse
from checkin.service import checkin_member, checkin_guest
from core.database import get_db
from core.qr import decode_qr
from members.service import get_user_by_cedula

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("", response_model=CheckinResponse)
def post_checkin(
    body: CheckinRequest,
    request: Request,
    x_device_id: str | None = Header(None, alias="X-Device-Id"),
    db: Session = Depends(get_db),
):
    device_id = x_device_id or request.client.host if request.client else "unknown"
    result = checkin_member(body.cedula, device_id, db)
    db.commit()
    return result


@router.post("/guest", response_model=CheckinResponse)
def post_guest_checkin(
    body: GuestCheckinRequest,
    request: Request,
    x_device_id: str | None = Header(None, alias="X-Device-Id"),
    db: Session = Depends(get_db),
):
    device_id = x_device_id or request.client.host if request.client else "unknown"
    result = checkin_guest(body.cedula_invitado, body.cedula_titular, device_id, db)
    db.commit()
    return result


@router.post("/qr", response_model=CheckinResponse)
def post_qr_checkin(
    qr_payload: str,
    request: Request,
    x_device_id: str | None = Header(None, alias="X-Device-Id"),
    db: Session = Depends(get_db),
):
    device_id = x_device_id or request.client.host if request.client else "unknown"
    decoded = decode_qr(qr_payload)
    if decoded is None:
        return {"resultado": "denegado", "razon": "QR_INVALIDO", "mensaje": "Código QR inválido."}
    cedula = decoded.get("cedula")
    if not cedula:
        return {"resultado": "denegado", "razon": "QR_INVALIDO", "mensaje": "Código QR inválido."}
    result = checkin_member(cedula, device_id, db)
    db.commit()
    return result
