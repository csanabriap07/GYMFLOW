"""
Router de members. Sin endpoints todavía — se agregan al implementar
spec/features/001, 004, 005, 006/.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/usuarios", tags=["members"])
