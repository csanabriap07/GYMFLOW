# 007 · Resumen de membresía — Tareas

- [ ] `membership/schemas.py`: `MembershipSummaryOut`.
- [ ] `membership/service.py`: `get_membership_summary(user_id, db)` (solo lectura, RF-04).
- [ ] `membership/router.py`: `GET /membership/summary` (kiosko, por cédula vía `members.service`).
- [ ] `checkin/service.py`: reutilizar el resumen en el semáforo de éxito (001/006).
- [ ] Frontend: tarjeta de resumen (kiosko + detalle staff).
- [ ] Tests: resumen de miembro activo, miembro vencido/sin plan, lectura sin efectos colaterales.
- [ ] Validar contra los criterios de aceptación de `spec.md`.
- [ ] Mover la feature a "Hecho" en `../../constitution/roadmap.md`.
