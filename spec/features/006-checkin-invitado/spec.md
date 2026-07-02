# 006 · Check-in de invitado

**Estado:** propuesta

**Traza:** HU-05 · **RN-04**, **RN-09**, **RN-10** · RF-05, RF-08

> **Atención (RN-04):** "el invitado ingresa **justo después del anfitrión**" implica una **secuencia/ventana temporal**, no solo verificar cupos. Ver Decisiones del plan y la duda abierta sobre la duración de la ventana.

## Qué hace

Permite que un **invitado** ingrese usando un **cupo de invitación** del socio titular. El sistema valida que el titular tenga membresía activa, cupos disponibles y que el invitado ingrese **justo después** de que el titular haya hecho su check-in; entonces descuenta **exactamente 1 cupo** del titular de forma atómica y registra el ingreso.

Mensaje objetivo (Propuesta): *"Bienvenido {nombre}. El socio {socio} tiene ahora {X} invitaciones restantes."*.

## Por qué

Convierte los "días de invitado" (hoy en papel/memoria) en un flujo con contabilidad real de cupos y aforo (problemática §1), evitando abuso del cupo cuando el titular no está presente (RN-04).

## Criterios de aceptación

- [ ] Dado un titular con membresía **activa** y `cupo_invitados_restantes > 0`, y que **acaba de hacer check-in** (dentro de la ventana temporal), cuando se registra a su invitado, entonces el acceso es **Exitoso**, se descuenta **exactamente 1** cupo del titular (RN-09) y se registra `CheckIn(Exitoso, usuario_id=invitado, titular_id=titular)` (RF-05).
- [ ] El descuento del cupo y el registro del `CheckIn` ocurren en **una única transacción** (RN-10): si falla el descuento, no hay acceso exitoso y se revierte todo.
- [ ] Si el titular **no ha ingresado justo antes** (no hay check-in exitoso suyo dentro de la ventana), el invitado es **Denegado** con motivo "el titular debe ingresar primero" (RN-04).
- [ ] Si el titular está **inactivo/vencido** o `cupo_invitados_restantes = 0` → **Denegado**, sin descontar (RN-04).
- [ ] El mensaje muestra los cupos restantes del titular tras el ingreso.

## Fuera de alcance

- **Cortesía de primer día** (persona sin titular) → `005-cortesia-primer-dia`.
- Gestión del catálogo de cupos por tipo → definido en `009` (`cupo_invitados` del `MembershipType`).
- **Dudas abiertas (marcar con el equipo/profesora):**
  - **Duración de la ventana temporal** de RN-04 ("justo después"): la doc no la especifica. Se propone **configurable, por defecto ≤10 min** desde el check-in exitoso del titular en el mismo dispositivo. Confirmar valor y si es por dispositivo o global.
  - **Dueño de la entidad `Guest`**: la constitución no la asigna explícitamente a un módulo. Se propone que la gestione `members` (es una persona). Confirmar.
