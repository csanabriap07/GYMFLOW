# 007 · Resumen de membresía — Plan

## Enfoque

Lógica de **lectura** en el módulo **`membership`** (dueño de `Membership` y `MembershipType`), reutilizada por `checkin` para enriquecer la respuesta del semáforo. `checkin` la obtiene llamando a `membership.service` (nunca a su repository).

## Implementación

1. `membership/service.py :: get_membership_summary(user_id, db)` → arma un DTO con tipo (join a `MembershipType`, tabla propia del módulo), `fecha_vencimiento`, estado, `visitas_restantes`, `cupo_invitados_restantes` y `proximo_pago` (= `fecha_vencimiento`).
2. `membership/schemas.py`: `MembershipSummaryOut`.
3. `membership/router.py`: `GET /membership/summary?cedula=` (kiosko, sin JWT de usuario) — resuelve la cédula vía `members.service` y devuelve el resumen.
4. `checkin/service.py`: tras un check-in exitoso (features 001/006), llama a `get_membership_summary` para el mensaje del semáforo.
5. Frontend: tarjeta de resumen en el kiosko y en la vista de detalle del staff.

## Decisiones

- **Resumen en `membership`, consumido por `checkin`** — la información pertenece al dominio de membresías; centralizarla evita duplicar el cálculo y respeta la regla de módulos.
- **`proximo_pago = fecha_vencimiento`** — el sistema no cobra (no es facturación, según la misión); el "próximo pago" es la fecha de fin de ciclo. Documentado.
- **Endpoint de kiosko sin login** — coherente con la misión (miembro no autentica); se resuelve por cédula.

## Riesgos

- **Miembro sin membresía** → devolver DTO con estado claro, no 404 abrupto en el kiosko.
- **Exposición de datos por cédula sin auth** → limitar el resumen a datos no sensibles (sin email/PII innecesaria) en el endpoint público del kiosko.
