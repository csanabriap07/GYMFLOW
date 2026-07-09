# 003 · Autenticación segura — Tareas

- [ ] `core/security.py`: hashing (bcrypt/argon2) + verificación (RN-12).
- [ ] `core/security.py`: emisión/decodificación de JWT con `exp` de 30 min (RN-11).
- [ ] `members/service.py`: `get_user_by_email(email, db)` reutilizable por `auth`.
- [ ] `auth/service.py`: `login(...)` (verifica hash, emite JWT). Sin repository propio.
- [ ] `auth/schemas.py` + `auth/router.py`: `POST /auth/login`.
- [ ] `core/security.py`: dependencias `get_current_user` y `require_role(*roles)` (RBAC, RF-09).
- [ ] Renovación deslizante del token en cada request autenticada.
- [ ] `.env.example` con `SECRET_KEY` (nunca commitear `.env`).
- [ ] Frontend: login de backoffice + interceptor Axios con Bearer.
- [ ] Tests: login ok, 401 credenciales inválidas, 403 rol insuficiente, expiración por inactividad, no-plaintext en DB, kiosko sin JWT.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
