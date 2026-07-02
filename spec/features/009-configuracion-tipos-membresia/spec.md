# 009 · Configuración de tipos de membresía

**Estado:** propuesta

**Traza:** HU-08 · RN-05, RN-06 · RF-11, RF-09 · depende de `003-autenticacion-segura`

## Qué hace

Da al **Administrador** un CRUD del catálogo de **tipos de membresía** (`MembershipType`): nombre, `precio_base`, `visitas_totales`, `cupo_invitados`, `duracion_dias`, `activo`. Impide eliminar/desactivar un tipo que tenga membresías activas vinculadas (RN-05) y asegura que editar sus parámetros no altere los contratos vigentes (RN-06).

## Por qué

Permite adaptar las reglas del negocio (planes) sin tocar código y sin romper los contratos ya vendidos. Es la base configurable sobre la que operan las membresías (`004`) y el check-in (`001`).

## Criterios de aceptación

- [ ] Un Administrador puede **crear** un tipo con `nombre`, `precio_base`, `visitas_totales`, `cupo_invitados`, `duracion_dias`, `activo` (RF-11).
- [ ] Un Administrador puede **editar** y **listar** tipos.
- [ ] Intentar **eliminar o desactivar** un tipo con **≥1 `Membership` activa** vinculada → **rechazado** con motivo claro (RN-05).
- [ ] Al **editar** los parámetros de un tipo, las `Membership` activas existentes **conservan sus valores** (no se recalculan `visitas_restantes` ni fechas); los nuevos valores aplican solo a **nuevas membresías / próximos ciclos** (RN-06). *Comprobable: editar `visitas_totales` no cambia el saldo de una membresía activa.*
- [ ] Todos los endpoints exigen rol **Administrador** (RBAC, RF-09).

## Fuera de alcance

- **Asignar** una membresía a un usuario → `004-gestion-usuarios` (aquí se define la plantilla, no se asigna).
- **Facturación/cobro** del `precio_base` → fuera de alcance del producto (misión).
