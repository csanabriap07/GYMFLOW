# 007 · Resumen de membresía

**Estado:** propuesta

**Traza:** HU-06 · RF-04 · (integra el semáforo de `001`)

## Qué hace

Muestra al miembro el estado de su membresía: **tipo**, **fecha de vencimiento**, **estado**, **visitas restantes**, **cupos de invitado restantes** y **fecha de próximo pago**. Se presenta en el semáforo verde tras un check-in exitoso y mediante un endpoint de consulta de solo lectura.

## Por qué

El usuario debe recibir feedback inmediato sobre su cuenta (problemática §1: falta de feedback), evitando las discusiones incómodas de la validación manual. Es puramente informativo.

## Criterios de aceptación

- [ ] Dado un miembro con membresía activa, cuando consulta su resumen (o completa un check-in exitoso), entonces se muestran: tipo de membresía, `fecha_vencimiento`, estado, `visitas_restantes`, `cupo_invitados_restantes` y próximo pago (RF-04).
- [ ] La consulta es de **solo lectura**: no descuenta visitas ni cupos ni registra ningún `CheckIn`.
- [ ] Un miembro sin membresía activa recibe un resumen coherente (estado Vencida / sin plan) sin error.

## Fuera de alcance

- **Descuento** de visitas/cupos → `001`/`006`.
- **Reportes agregados** para administración → `010-reportes-asistencia`.
- Autogeneración de **QR** del miembro → relacionado con `008`; aquí no se emite QR.
