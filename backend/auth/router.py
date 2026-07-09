"""
Router de auth. Sin endpoints todavía — se agregan al implementar
spec/features/003-autenticacion-segura/.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
