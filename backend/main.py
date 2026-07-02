"""
Único punto de integración entre módulos (AGENTS.md): registra todos los
routers. No debe contener lógica de negocio.
"""
from fastapi import FastAPI

from auth.router import router as auth_router
from members.router import router as members_router
from checkin.router import router as checkin_router
from membership.router import router as membership_router
from reports.router import router as reports_router

app = FastAPI(title="GymFlow API")

app.include_router(auth_router)
app.include_router(members_router)
app.include_router(checkin_router)
app.include_router(membership_router)
app.include_router(reports_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
