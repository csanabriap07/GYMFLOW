# Tech stack y convenciones

> ⚠️ La Propuesta original lista "Prisma" como ORM con una justificación que describe Node.js/Express — es un error de copiado (Prisma no aplica a FastAPI/Python). Este documento asume **SQLAlchemy + Alembic**, que es lo que aparece en el Diseño Preliminar y en el diagrama de arquitectura ya validado. Confirmar con el equipo/profesora antes de seguir si hay duda.

## Tecnologías

- **Lenguaje:** Python 3.12+ (backend), TypeScript (frontend)
- **Framework / runtime backend:** FastAPI
- **Framework frontend:** React 18 + Vite, Tailwind CSS
- **Consumo de API en frontend:** React Query + Axios
- **Base de datos:** PostgreSQL
- **ORM / migraciones:** SQLAlchemy + Alembic
- **Auth:** JWT propio (sin OAuth2 Authorization Server), solo para roles Staff/Administrador
- **Tests:** pytest (backend) — a definir framework de tests frontend con el equipo
- **Despliegue:** Docker (contenedorizado, requisito RNF de despliegue)

## Archivos / módulos clave (Monolito Modular)

- `core/` — config, conexión a base de datos, seguridad JWT, dependencias compartidas.
- `auth/` — router + service + schemas. **No tiene repository propio**: reutiliza el repository de `members` para leer `User` (no duplica acceso a esa tabla).
- `members/` — router, service, repository, schemas. Dueño de la tabla `User`.
- `checkin/` — router, service, repository, schemas. Dueño de la tabla `CheckIn`. Orquesta la validación de RN-01 a RN-04.
- `membership/` — router, service, repository, schemas. Dueño de `Membership` y `MembershipType`.
- `reports/` — router, service, repository, schemas. Lectura agregada sobre `CheckIn` para reportes.
- `models/` — modelos SQLAlchemy centralizados (`User`, `Membership`, `MembershipType`, `CheckIn`, `Guest`).
- `main.py` — registra todos los routers, único punto de integración entre módulos.

## Comandos

- `uvicorn main:app --reload` — arranca el backend en desarrollo.
- `alembic revision --autogenerate -m "<mensaje>"` / `alembic upgrade head` — migraciones.
- `pytest` — corre tests de backend.
- `npm run dev` — arranca el frontend (Vite).
- `docker compose up` — levanta el stack completo (a definir servicios exactos con el equipo DevOps).

## Modelo de datos / dominio

- `User` — cédula, nombre, email, rol (Invitado/Miembro/Empleado/Administrador), estado (Activo/Inactivo). Al eliminar un usuario se borra su info personal pero se preservan sus `CheckIn` históricos (RN-07).
- `Membership` — vinculada a `User` (miembro_id), tipo, `visitas_restantes`, `cupo_invitados_restantes`, `fecha_inicio`, `fecha_vencimiento`, estado (Activa/Vencida).
- `MembershipType` — plantilla configurable: nombre, precio_base, visitas_totales, cupo_invitados, duracion_dias, activo. **No se puede eliminar/desactivar si tiene membresías activas vinculadas** (RN-05). Cambios en sus parámetros no alteran contratos vigentes, solo aplican al siguiente ciclo (RN-06).
- `CheckIn` — usuario_id, fecha_hora, resultado (Exitoso/Denegado), razon_denegacion, titular_id (solo si es check-in de invitado). Registro inmutable.
- `Guest` (Invitado) — cédula, nombre, titular_id (el miembro que lo invita).

## Convenciones

- **Regla de módulos (no negociable):** cada módulo solo accede a sus propias tablas vía su `repository.py`. Si un módulo necesita datos de otro (ej. `checkin` necesita saber si la `membership` está activa), llama al `service.py` del módulo dueño — nunca consulta la tabla directamente ni importa su repository.
- Nombres: `snake_case` en Python, `camelCase` en TypeScript/React.
- Validación de entrada con Pydantic schemas (`schemas.py` por módulo), nunca validar a mano en el router.
- Todo endpoint que descuente visitas o cupos de invitado debe envolver la operación en una transacción (RN-10) — no hacer el `SELECT` y el `UPDATE` en pasos separados sin lock/transacción.
- Idioma del contenido: nombres de entidades y campos en español (como en el análisis), nombres de variables/funciones de código en inglés, consistente con lo ya definido en el diagrama de clases.

## Estilo visual

- Kiosko de check-in: botones táctiles ≥48x48px, alto contraste, legible a 1 metro de distancia (RNF de usabilidad).
- Backoffice/admin: puede ser más denso en información, prioriza tablas y filtros sobre botones grandes.
- Tailwind CSS como sistema de utilidades; sin librería de componentes definida aún (a decidir con el equipo Frontend).

## Límites duros

- No agregar Spring/OAuth2 Authorization Server, login federado, ni multi-`SecurityFilterChain` — el auth es JWT propio y simple.
- No introducir microservicios ni comunicación entre servicios — es un monolito modular por decisión explícita del equipo.
- No hacer queries cruzadas entre tablas de distintos módulos saltándose el service del módulo dueño.
- No guardar contraseñas en texto plano — siempre hash (RN-12).
- No exponer `.env` ni credenciales de base de datos en el repo.
- Toda conexión debe ir sobre HTTPS/TLS en producción (RNF de seguridad).
