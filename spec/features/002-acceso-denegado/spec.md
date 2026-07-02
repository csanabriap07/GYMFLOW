# 002 · Acceso denegado

**Estado:** propuesta

**Traza:** HU-02 · RN-01 (condición inversa), RN-02, **RN-03**, RN-10 · RF-05, RF-06 · RNF usabilidad (mensaje claro), principio "mensajes claros"

> **Decisión de alcance (RN-03):** el bloqueo de dispositivo tras 3 intentos fallidos vive aquí, no en una feature aparte. Justificación: RN-03 se dispara exactamente sobre **intentos de check-in denegados**, que es el dominio de esta feature. Alternativa considerada (feature independiente) anotada en `roadmap.md`. **Duda abierta:** identidad del dispositivo (ver Fuera de alcance / Decisiones del plan).

## Qué hace

Cuando la validación de un check-in falla, el kiosko muestra un semáforo **rojo** con el motivo exacto del rechazo (membresía vencida o sin visitas) y la fecha del próximo pago, sin ambigüedad. Además, tras **3 intentos fallidos consecutivos en ≤5 min** desde el mismo dispositivo, el kiosko queda **bloqueado 20 min** (RN-03) como control anti-abuso.

Mensaje objetivo (Propuesta): *"ACCESO DENEGADO. Ha alcanzado el límite mensual. Próximo pago: {fecha}"*.

## Por qué

El usuario del kiosko no debe quedar en duda de por qué se le negó el acceso (principio de la misión). Y sin un límite de intentos, el kiosko queda expuesto a tanteo de cédulas; RN-03 lo mitiga.

## Criterios de aceptación

- [ ] Dado un miembro con membresía **vencida** (hoy > `fecha_vencimiento`) o `visitas_restantes = 0`, cuando intenta check-in, entonces el resultado es **Denegado**, semáforo rojo, con motivo claro + "Próximo pago: {fecha}" (RN-01 inversa).
- [ ] Un intento denegado **no** altera `visitas_restantes` ni ningún saldo (RN-10: sin efectos colaterales) y **sí** persiste `CheckIn(resultado=Denegado, razon_denegacion)` (RF-05).
- [ ] La `razon_denegacion` distingue al menos: `MEMBRESIA_VENCIDA`, `SIN_VISITAS`, `YA_INGRESO_HOY` (RN-02), `DISPOSITIVO_BLOQUEADO`.
- [ ] 3 intentos fallidos consecutivos desde el mismo dispositivo en ≤5 min → dispositivo **bloqueado 20 min**; durante el bloqueo el kiosko muestra mensaje de bloqueo y **no** procesa check-ins (RN-03).
- [ ] Un check-in **exitoso reinicia** el contador de intentos fallidos consecutivos del dispositivo.
- [ ] Los mensajes son legibles a 1m y sin jerga técnica (RNF usabilidad).

## Fuera de alcance

- Cálculo/registro del **camino feliz** (éxito + descuento) → `001-checkin-membresia-activa`.
- Denegación específica del **invitado** (titular inactivo / sin cupos / fuera de ventana) → `006-checkin-invitado`.
- **Duda abierta a confirmar con el equipo:** cómo se identifica el "dispositivo" (header `X-Device-Id` emitido por el kiosko vs. IP de origen). El plan asume `X-Device-Id` con fallback a IP.
