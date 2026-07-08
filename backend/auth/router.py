from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.schemas import LoginRequest, TokenResponse
from auth.service import login
from core.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def post_login(body: LoginRequest, db: Session = Depends(get_db)):
    result = login(body.email, body.password, db)
    return result
