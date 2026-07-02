"""
Router de reports. Sin endpoints todavía — se agregan al implementar
spec/features/010-reportes-asistencia/.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/reportes", tags=["reports"])
