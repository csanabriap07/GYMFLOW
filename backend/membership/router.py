"""
Router de membership. Sin endpoints todavía — se agregan al implementar
spec/features/001, 007, 009/.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/membresias", tags=["membership"])
