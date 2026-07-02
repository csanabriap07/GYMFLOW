# 002 · Acceso denegado — Tareas

- [ ] `checkin/schemas.py`: enum `RazonDenegacion` + DTO de respuesta denegada.
- [ ] `checkin/service.py`: devolver `Denegado` + motivo para RN-01 inversa y RN-02.
- [ ] `models/` + migración Alembic: tabla `CheckinDeviceLock`.
- [ ] `checkin/repository.py`: `register_failed_attempt`, `reset_attempts`, `is_locked`.
- [ ] `checkin/router.py`: dependencia `enforce_device_not_locked` (X-Device-Id / IP) en endpoints de check-in.
- [ ] Lógica RN-03: 3 fallos en ≤5 min → `bloqueado_hasta = now+20min`; éxito resetea contador.
- [ ] Endpoint protegido (rol staff, feature 003) para **desbloquear** dispositivo manualmente.
- [ ] Frontend: semáforo rojo con motivo + pantalla de bloqueo con cuenta regresiva.
- [ ] Tests: vencida, sin visitas, ya ingresó hoy, 3 fallos→bloqueo, éxito resetea, denegado no toca saldos.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
