# 004 · Gestión de usuarios

**Estado:** propuesta

**Traza:** HU-07 · RN-07, RN-12 · RF-10, RF-09 · depende de `003-autenticacion-segura`

## Qué hace

Da al **Staff** (Empleado/Administrador) un CRUD de usuarios y la posibilidad de asignar/gestionar la **membresía** de un usuario, para mantener actualizada la base de datos. Incluye el borrado de usuarios respetando la preservación del histórico de check-ins.

## Por qué

Sin altas manuales no hay miembros que validar en el kiosko; es la base operativa del Sprint 1 (HU-07) y prerrequisito real de los flujos de check-in.

## Criterios de aceptación

- [ ] Un Staff autenticado puede **crear** un usuario (`cédula`, `nombre`, `email`, `rol`, `estado`) y el perfil queda persistido (RF-10).
- [ ] Un Staff puede **leer, listar y editar** usuarios.
- [ ] Un Staff puede **asignar una membresía** a un usuario miembro (vinculando un `MembershipType` existente y creando su `Membership` con saldos iniciales).
- [ ] Al **eliminar** un usuario, su información personal (`cédula`, `nombre`, `email`) se borra de forma irreversible, **pero** sus registros de `CheckIn` históricos se preservan (RN-07). *Comprobable: tras el borrado, los `CheckIn` del usuario siguen existiendo para estadística.*
- [ ] Si se crea un usuario Empleado/Administrador con credenciales, la contraseña se guarda **hasheada** (RN-12).
- [ ] Todos los endpoints exigen rol Empleado/Administrador (RBAC, RF-09); sin token válido → 401/403.

## Fuera de alcance

- **Autenticación** (login, emisión de JWT, RBAC) → `003-autenticacion-segura`.
- **CRUD de tipos de membresía** (`MembershipType`) → `009-configuracion-tipos-membresia` (aquí se **asignan**, no se definen).
- **Duda abierta (RN-07):** se implementa como **anonimización/tombstone** de la fila `User` (se vacía la PII y se conserva el `id`) para no romper la FK `CheckIn.usuario_id`. Alternativa (borrado físico con `usuario_id` nulo) descartada por trazabilidad. Confirmar con el equipo.
