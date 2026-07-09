# 004 · Gestión de usuarios — Plan

## Enfoque

El módulo **`members`** es dueño de la tabla `User` y expone el CRUD completo (`router/service/repository/schemas`). Para **asignar una membresía** (que vive en otra tabla) llama a `membership.service.create_membership(...)` — nunca toca la tabla `Membership` ni su repository. El borrado respeta RN-07 anonimizando la fila en vez de eliminarla físicamente.

## Implementación

1. `members/schemas.py`: `UserCreate`, `UserUpdate`, `UserOut` (validación Pydantic; `rol` y `estado` como enums de la constitución).
2. `members/repository.py`: `create`, `get`, `list`, `update`, `anonymize` sobre `User`.
3. `members/service.py`: reglas de negocio del CRUD + `anonymize_user(user_id, db)` (RN-07): vacía `cedula/nombre/email`, marca `estado=Inactivo`, conserva `id`.
4. **Asignar membresía:** `members.service.assign_membership(user_id, tipo_id, db)` → delega en `membership.service.create_membership(...)` (crea `Membership` con `visitas_restantes = tipo.visitas_totales`, `cupo_invitados_restantes = tipo.cupo_invitados`, fechas según `duracion_dias`).
5. Si el usuario es staff con login: `core.security.hash_password` al persistir (RN-12).
6. `members/router.py`: endpoints `POST/GET/PUT/DELETE /users`, todos con `Depends(require_role("Empleado","Administrador"))`.
7. Frontend backoffice: tabla de usuarios densa con filtros + formularios de alta/edición.

## Decisiones

- **Anonimización en lugar de `DELETE` físico (RN-07)** — preserva la integridad referencial con `CheckIn` (dueño: `checkin`) sin que `members` tenga que tocar esa tabla. Se descarta `ON DELETE SET NULL` porque perdería la asociación histórica útil para estadística.
- **Asignación de membresía vía `membership.service`** — respeta la regla de módulos (no cruzar a la tabla `Membership`).
- **Snapshot de saldos al asignar** — `visitas_restantes`/`cupo_invitados_restantes` se copian del `MembershipType` al crear la `Membership`, habilitando RN-06 (cambios del tipo no afectan contratos vigentes).

## Riesgos

- **PII en logs** — evitar loguear cédula/email; revisar antes de la entrega.
- **Borrado de usuario con membresía activa** — decidir si se bloquea o se anonimiza igualmente; por defecto se permite anonimizar (el histórico se preserva). Documentar.
- **Consistencia de enums** `rol`/`estado` entre backend y frontend.
