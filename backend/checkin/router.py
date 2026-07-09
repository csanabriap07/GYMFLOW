"""
Router de checkin. Sin endpoints todavía — se agregan al implementar
spec/features/001, 002, 005, 006/.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/checkin", tags=["checkin"])
