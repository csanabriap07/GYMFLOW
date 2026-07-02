# 001 · Check-in con membresía activa

**Estado:** propuesta

**Traza:** HU-01 · RN-01, RN-02, RN-08, RN-10 · RF-01, RF-04, RF-05, RF-06, RF-08 · RNF rendimiento (≤3s, ≥10 concurrencia), RNF usabilidad táctil (≥48×48px, legible a 1m)

## Qué hace

En el kiosko táctil, un miembro se identifica con su cédula. El sistema valida en tiempo real que su membresía esté activa y con visitas disponibles y, si procede, registra el ingreso descontando exactamente una visita, mostrando un semáforo verde con su nombre y las visitas que le restan.

Mensaje objetivo (Propuesta): *"ACCESO PERMITIDO. Bienvenido/a {nombre}. Visitas restantes: {X}"*.

## Por qué

Es el flujo central del producto (HU-01) y la razón de ser del sistema: reemplaza la validación manual en recepción por un motor de reglas que resuelve en ≤3s. Todo el resto del kiosko (denegación, invitado, cortesía) se construye sobre este camino feliz.

## Criterios de aceptación

- [ ] Dado un miembro con membresía activa (hoy ≤ `fecha_vencimiento`) y `visitas_restantes > 0`, cuando ingresa su cédula válida, entonces el resultado es **Exitoso** y se muestra semáforo verde con nombre y visitas restantes (RN-01).
- [ ] Un check-in exitoso descuenta **exactamente 1** de `visitas_restantes` de su membresía (RN-08) y persiste un `CheckIn(resultado=Exitoso, fecha_hora, usuario_id)` (RF-05).
- [ ] La validación, el registro del `CheckIn` y el descuento ocurren en **una única transacción**; si el descuento falla, no queda ningún `CheckIn` marcado Exitoso ni visita descontada (RN-10). *Comprobable con un test que fuerza un fallo a mitad de la transacción.*
- [ ] Un segundo intento del **mismo miembro el mismo día calendario** no descuenta otra visita y comunica que ya registró su ingreso hoy (RN-02).
- [ ] El flujo resuelve en ≤3s bajo condiciones normales y soporta ≥10 check-ins concurrentes sin descontar de más (RNF rendimiento + RN-10).
- [ ] Los elementos accionables del kiosko miden ≥48×48px y el mensaje es legible a 1m (RNF usabilidad).

## Fuera de alcance

- Mensajería y flujo de **denegación** (membresía vencida / sin visitas) y bloqueo de dispositivo → `002-acceso-denegado`.
- Identificación por **QR o nombre** → `008-busqueda-multiples-criterios` (aquí solo por cédula, RF-01).
- **Cortesía de primer día** para cédulas no registradas → `005-cortesia-primer-dia`.
- **Invitados** → `006-checkin-invitado`.
- Panel de **resumen** ampliado de membresía → `007-resumen-membresia` (aquí solo el mínimo del semáforo).
