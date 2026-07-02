# 005 · Cortesía de primer día

**Estado:** propuesta

**Traza:** HU-04 · RF-07 · RN-10, RN-02, RF-05

> **Nota de trazabilidad:** en `Analisis.docx` los criterios de aceptación de HU-04 están copiados de otra HU (describen una búsqueda, no la cortesía). Esta spec usa la descripción correcta de la Propuesta (§2.A) y de RF-07. Marcado para el equipo.

## Qué hace

En el kiosko, si la **cédula no existe** en la base de datos, el sistema concede **un** acceso gratuito único, da de alta al usuario como **Prospecto** y **impide un segundo acceso gratuito** con esa misma cédula.

## Por qué

Convierte el "primer día gratis" (hoy gestionado con papel/memoria) en un flujo controlado y contabilizado, habilitando la conversión de prospectos a miembros (problemática §1 de la Propuesta).

## Criterios de aceptación

- [ ] Dada una cédula **no registrada**, cuando se hace check-in, entonces el sistema crea un `User` marcado como **Prospecto** y registra un `CheckIn` **Exitoso** de cortesía, mostrando semáforo verde de bienvenida (RF-07).
- [ ] La creación del prospecto y el registro del `CheckIn` ocurren en **una única transacción** (RN-10): si algo falla, no queda un prospecto "a medias" ni un check-in huérfano.
- [ ] Un **segundo** intento con una cédula que **ya usó** su cortesía → **no** concede otra cortesía; deniega con motivo claro (p. ej. "cortesía de primer día ya utilizada") e invita a afiliarse.
- [ ] Un prospecto que **ya usó** la cortesía no puede convertirla en accesos recurrentes por el kiosko (solo tras afiliarse en `004`).

## Fuera de alcance

- **Afiliación / asignación de membresía** al prospecto → `004-gestion-usuarios`.
- **Invitado de un socio** (cupos) → `006-checkin-invitado` (flujo distinto).
- **Dudas abiertas:**
  - El enum `rol` de `User` es `Invitado/Miembro/Empleado/Administrador` y **no incluye "Prospecto"**. Se propone marcar la cortesía con un `estado`/flag `cortesia_usada` (o rol `Invitado` + flag) en lugar de añadir un valor de enum, para no romper el modelo. Confirmar con el equipo.
  - En el kiosko solo se captura la **cédula**; el `nombre` del prospecto puede quedar pendiente de completar por staff. Confirmar captura mínima.
