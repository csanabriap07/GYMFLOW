from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.security import verify_password, create_access_token
from members.service import get_user_by_email


def login(email: str, password: str, db: Session) -> dict:
    user = get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": str(user.id), "rol": user.rol})
    return {"access_token": token, "rol": user.rol}
