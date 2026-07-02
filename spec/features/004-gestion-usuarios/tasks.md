# 004 · Gestión de usuarios — Tareas

- [ ] `members/schemas.py`: `UserCreate/UserUpdate/UserOut` con enums de `rol`/`estado`.
- [ ] `members/repository.py`: `create/get/list/update/anonymize` sobre `User`.
- [ ] `members/service.py`: CRUD + `anonymize_user` (RN-07).
- [ ] `members/service.py`: `assign_membership(...)` delegando en `membership.service.create_membership(...)`.
- [ ] `membership/service.py`: `create_membership(user_id, tipo_id, db)` con snapshot de saldos y fechas.
- [ ] Hash de contraseña al crear staff con login (RN-12).
- [ ] `members/router.py`: endpoints CRUD protegidos por `require_role` (RF-09).
- [ ] Frontend: tabla + formularios de usuarios (backoffice denso).
- [ ] Tests: alta, edición, borrado→PII eliminada + CheckIn conservados (RN-07), asignación de membresía, RBAC 401/403.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
