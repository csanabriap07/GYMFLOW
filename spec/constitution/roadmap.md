# Roadmap

> Basado en el mapa de historias de usuario y la planeación de 3 sprints de la Propuesta. Cada feature se crea en `features/NNN-nombre-feature/` con `spec.md`, `plan.md` y `tasks.md` antes de tocar código.

## Sprint 1 (Alta prioridad — base del sistema)

3. **001 · Check-in con membresía activa** — HU-01. Validar cédula, calcular visitas restantes, registrar el check-in. *(feature de ejemplo ya creada, ver `features/001-checkin-membresia-activa/`)*
4. **002 · Acceso denegado** — HU-02. Mensaje claro de rechazo cuando la membresía está vencida o sin visitas.
5. **003 · Autenticación segura** — HU-10. Login de Empleado/Administrador con JWT y control por rol.
6. **004 · Gestión de usuarios** — HU-07. CRUD de usuarios y membresías para el staff.

## Sprint 2 (Alta/Media — invitados y experiencia)

7. **005 · Cortesía de primer día** — HU-04. Alta automática como "Prospecto" con acceso gratuito único.
8. **006 · Check-in de invitado** — HU-05. Descuento atómico de cupo de invitado del socio titular.
9. **007 · Resumen de membresía** — HU-06. Detalle de tipo, vencimiento y visitas restantes.
10. **008 · Búsqueda por múltiples criterios** — HU-03. Búsqueda por cédula, QR o nombre.

## Sprint 3 (Media/Baja — administración y reportes)

11. **009 · Configuración de tipos de membresía** — HU-08. CRUD de `MembershipType` respetando RN-05/RN-06.
12. **010 · Reportes de asistencia** — HU-09. Reporte histórico con filtro por rango de fechas y export a XLSX/CSV.

## Semana de documentación

- Consolidar `docs/` y `spec/` finales para entrega.
- Verificar trazabilidad: cada HU → su feature → sus criterios de aceptación cumplidos.

## Backlog / ideas 💡

- Bloqueo de dispositivo tras 3 intentos fallidos en 5 min (RN-03) — **decisión:** se implementa dentro de `002-acceso-denegado` como guard de dispositivo del módulo `checkin` (el contador vive donde se producen las denegaciones), no como feature independiente. Ver `features/002-acceso-denegado/`. Queda abierta la confirmación de la *identidad de dispositivo* (header `X-Device-Id` vs IP) con el equipo/profesora.
- Multi-sede — explícitamente fuera de alcance (ver `mission.md`), no planear a menos que cambie el alcance del proyecto.
