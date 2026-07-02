# Misión

## Qué construimos

GymFlow es un sistema de control de acceso físico y gestión de membresías para gimnasios pequeños y medianos, que reemplaza la validación manual (planillas/Excel) en recepción por un motor de reglas de negocio que valida en tiempo real.

1. **Check-in (Kiosko táctil)** — búsqueda por cédula/QR/nombre, validación de membresía activa, cortesía de primer día, check-in de invitados con descuento atómico de cupos.
2. **Feedback visual** — pantalla de semáforo (permitido/denegado) con mensaje claro para el usuario y el staff, sin ambigüedad sobre el motivo de un rechazo.
3. **Backoffice (Administración)** — CRUD de usuarios y tipos de membresía, reportes de asistencia con exportación a XLSX/CSV.

## Para quién

- **Miembro (socio)** — usuario con membresía activa que hace check-in sin intervención del staff.
- **Invitado** — persona sin membresía propia que ingresa con el cupo de un socio, o accede una única vez por cortesía de primer día.
- **Empleado / Staff (recepción)** — resuelve incidencias del kiosko y registra usuarios manualmente.
- **Administrador / Dueño** — accede a reportes y configura parámetros globales (tipos de membresía, límites de invitados).

## Principios

- **Real time y sin fricción** — el flujo de check-in debe resolver en ≤3s (RNF de rendimiento); nada de pasos innecesarios en el kiosko táctil.
- **Atomicidad ante todo** — cualquier operación que descuente visitas o cupos de invitado debe ser ACID: si el descuento falla, el check-in no se registra como exitoso (RN-10).
- **Modularidad por dominio, no por capa técnica** — el monolito se organiza en módulos (`auth`, `members`, `checkin`, `membership`, `reports`) con dueño claro, no en una carpeta gigante de controllers/services mezclados. Esto también da ownership natural a los 5 integrantes del equipo.
- **Mensajes claros antes que "elegantes"** — el usuario del kiosko no debe quedar en duda de por qué se le negó el acceso; siempre se explica el motivo (RN sobre feedback visual).
- **Táctil primero** — toda decisión de UI en el flujo de kiosko prioriza pantalla táctil (botones ≥48x48px, legibilidad a 1m), el backoffice puede ser más denso.

## Qué NO es

- No es un sistema de facturación/cobro en línea — no hay pasarela de pagos ni checkout, solo se registra `precio_base` como dato de referencia.
- No es multi-sede con sincronización entre gimnasios — se diseña para una sede; si el alcance real incluye varias sedes, hay que replantear esta constitución antes de seguir.
- No es una app móvil nativa — es una PWA responsive (kiosko en tablet + panel admin en navegador Chromium).
- No requiere Authorization Server ni login federado (Google/GitHub) — la autenticación es JWT propio y simple, solo para roles Staff/Administrador (el flujo de Miembro/Invitado no requiere login).
