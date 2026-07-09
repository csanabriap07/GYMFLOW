# 003 · Autenticación segura — Plan

## Enfoque

Módulo **`auth`** con `router.py`, `service.py` y `schemas.py` pero **sin `repository.py` propio**: para leer `User` reutiliza `members.service` (no duplica acceso a la tabla `User`, según la constitución). Las primitivas de hashing y JWT viven en `core/security.py` y se exponen como **dependencias** de FastAPI para RBAC.

## Implementación

1. `core/security.py`: `hash_password`/`verify_password` (passlib, bcrypt o argon2) y `create_access_token`/`decode_token` (python-jose). Clave secreta desde `.env` (nunca en el repo).
2. `auth/service.py :: login(credenciales, db)`: `members.service.get_user_by_email(email, db)` → `verify_password` → si ok, emite JWT con `sub`, `rol`, `exp = now + 30min`.
3. `core/security.py`: dependencias `get_current_user(token)` y `require_role(*roles)` para proteger routers.
4. **Expiración deslizante (RN-11):** middleware/dependencia que, en cada request autenticada válida, re-emite el token con `exp` renovado a +30min (o instruye al frontend a refrescarlo). Sin actividad 30 min → token vencido → 401.
5. `auth/router.py`: `POST /auth/login`. Los routers de `004/009/010` añaden `Depends(require_role("Empleado"|"Administrador"))`.
6. Frontend: pantalla de login (solo backoffice) + almacenamiento del token + interceptor Axios que adjunta `Authorization: Bearer`.

## Decisiones

- **`auth` sin repository** — cumple la constitución: la tabla `User` tiene un único dueño (`members`). `auth` orquesta sobre `members.service`.
- **Hash con bcrypt/argon2 vía passlib** — estándar, sin texto plano (RN-12). Se descarta cualquier cifrado reversible.
- **Expiración deslizante en vez de refresh token** — más simple para el alcance; se marca como duda a confirmar.
- **RBAC por dependencia** (`require_role`) — declarativo por endpoint; se descarta lógica de permisos dispersa en cada handler.

## Riesgos

- **Fuga de secreto JWT** — mitigación: `SECRET_KEY` en `.env`, fuera del repo (límite duro); rotación documentada.
- **HTTPS obligatorio en prod** (RNF) — el JWT viaja en claro si no hay TLS; documentar despliegue tras TLS 1.3.
- **Diferencia inactividad vs. expiración fija** — cubrir con test la renovación deslizante.
