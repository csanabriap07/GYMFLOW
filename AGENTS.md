# GymFlow

Sistema de control de acceso físico y gestión de membresías para gimnasios pequeños y medianos. Reemplaza la validación manual en recepción (planillas/Excel) por un motor de reglas que valida el ingreso en tiempo real desde un kiosko táctil, con un backoffice para administrar usuarios, membresías y reportes. Proyecto académico de Ingeniería de Software II (equipo de 5, entrega en 1 semana).

La fuente de verdad del diseño es `spec/`. Este archivo no repite ese contenido, lo indexa (ver **Documentación**).

## Stack

- **Lenguaje:** Python 3.12+ (backend), TypeScript (frontend)
- **Framework / runtime:** FastAPI (backend), React 18 + Vite (frontend)
- **Base de datos:** PostgreSQL con SQLAlchemy + Alembic (ORM y migraciones)
- **Dependencias / entorno:** Pipenv — entorno virtual aislado por proyecto (`Pipfile` / `Pipfile.lock`)
- **Estilos / UI:** Tailwind CSS · consumo de API con React Query + Axios
- **Auth:** JWT propio y simple, solo para roles Staff/Administrador
- **Tests:** pytest (backend); framework de tests frontend a definir con el equipo
- **Despliegue:** Docker (contenedorizado)

## Comandos

**Dependencias (Pipenv) — todo queda instalado en el entorno del proyecto, nunca global:**

- `pipenv install` — instala las dependencias del proyecto desde `Pipfile`/`Pipfile.lock`
- `pipenv install --dev` — instala también las dependencias de desarrollo (tests, lint)
- `pipenv install <paquete>` — añade una librería nueva (actualiza `Pipfile` y `Pipfile.lock`)
- `pipenv install --dev <paquete>` — añade una dependencia solo de desarrollo
- `pipenv shell` — abre una shell dentro del entorno del proyecto
- `pipenv run <comando>` — ejecuta un comando puntual dentro del entorno

**Backend (dentro del entorno de Pipenv):**

- `pipenv run uvicorn main:app --reload` — arranca el backend en local
- `pipenv run pytest` — ejecuta los tests de backend (deben pasar antes de cada commit)
- `pipenv run alembic revision --autogenerate -m "<mensaje>"` / `pipenv run alembic upgrade head` — crea y aplica migraciones

**Frontend:**

- `npm run dev` — arranca el frontend (Vite)
- `npm run build` — compila el frontend para producción

**Stack completo:**

- `docker compose up` — levanta el stack completo

**Lint:** herramienta a definir con el equipo (p. ej. `ruff`, instalable con `pipenv install --dev ruff`); acordar antes de exigirla en PR.

## Estructura del proyecto

Monorepo: `backend/` (FastAPI) y `frontend/` (React) como paquetes separados, con `spec/` y `docs/` compartidos en la raíz.

- `backend/` — API FastAPI, monolito modular. Cada módulo agrupa `router` + `service` + `repository` + `schemas` por dominio de negocio:
  - `backend/core/` — config, conexión a base de datos, seguridad JWT y dependencias compartidas
  - `backend/auth/` — router + service + schemas. **No tiene repository propio**: reutiliza el de `members` para leer `User`
  - `backend/members/` — dueño de la tabla `User`
  - `backend/checkin/` — dueño de la tabla `CheckIn`; orquesta la validación del ingreso (RN-01 a RN-04)
  - `backend/membership/` — dueño de `Membership` y `MembershipType`
  - `backend/reports/` — lectura agregada para reportes de asistencia
  - `backend/models/` — modelos SQLAlchemy centralizados (`User`, `Membership`, `MembershipType`, `CheckIn`, `Guest`)
  - `backend/main.py` — registra todos los routers; único punto de integración entre módulos
  - `backend/Pipfile` · `backend/Pipfile.lock` — dependencias del backend (Pipenv)
  - `backend/alembic/` — migraciones de base de datos
- `frontend/` — kiosko táctil (check-in) y panel de backoffice (React + Vite + Tailwind)
- `spec/` — especificación del proyecto (`constitution/` + `features/`)
- `docs/` — material fuente original (propuesta, análisis, diagramas), para trazabilidad
- `AGENTS.md` — reglas para agentes; fuente única, la lee OpenCode de forma nativa
- `CLAUDE.md` — puntero a `AGENTS.md` para Claude Code (`@AGENTS.md`)
- `.claude/skills/` — skills compartidas (Claude Code las usa nativamente; OpenCode las lee por compatibilidad)
- `docker-compose.yml` — stack completo

## Convenciones

- **Regla de módulos (no negociable):** cada módulo accede solo a sus propias tablas vía su `repository`. Si necesita datos de otro módulo, llama al `service` del módulo dueño — nunca consulta su tabla ni importa su `repository`.
- **Validación con Pydantic** (`schemas.py` por módulo); nunca validar a mano en el `router`.
- **Atomicidad (RN-10):** toda operación que descuente visitas o cupos de invitado va envuelta en una transacción; no separar `SELECT` y `UPDATE` sin lock/transacción.
- **Nombres:** `snake_case` en Python, `camelCase` en TypeScript/React.
- **Idioma:** nombres de entidades y campos en español; variables y funciones de código en inglés.
- **Tests al lado del código del módulo**, corriendo con `pytest`.
- **Kiosko táctil primero:** botones ≥48×48px, alto contraste, legible a 1m. El backoffice puede ser más denso.

## No hagas

- **No agregues OAuth2 Authorization Server ni login federado (Google/GitHub).** El auth es JWT propio y simple, solo para Staff/Administrador; el flujo de Miembro/Invitado en el kiosko no requiere login.
- **No introduzcas microservicios** ni comunicación entre servicios: es un monolito modular por decisión del equipo.
- **No hagas queries cruzadas** entre tablas de módulos distintos saltándote el `service` del módulo dueño.
- **No instales librerías con `pip` suelto ni de forma global.** Toda dependencia se añade con `pipenv install` para que quede aislada en el proyecto y registrada en `Pipfile`/`Pipfile.lock`. No edites `Pipfile.lock` a mano ni subas el entorno virtual (`.venv`) al repositorio.
- **No guardes contraseñas en texto plano** — siempre hash (RN-12).
- **No expongas `.env` ni credenciales** de base de datos en el repositorio.
- **No amplíes el alcance** a multi-sede, pasarela de pagos/checkout ni app móvil nativa: están explícitamente fuera de alcance (ver `spec/constitution/mission.md`).
- **No inventes reglas de negocio** que no estén en `docs/` o en `spec/constitution/`. Si una HU es ambigua, señálalo en vez de asumir.

## Flujo de trabajo

- Antes de implementar una feature, verifica que existe su `spec.md` en `spec/features/`. Si no existe, genérala primero (plantilla en `spec/README.md`) y confirma antes de pasar a `plan.md`/código.
- Antes de implementar, **revisa la carpeta de skills** (ver **Herramientas del agente**): si hay una skill aplicable a la tarea, léela y síguela antes de escribir código.
- Antes de una tarea no trivial, propón un plan y espera mi OK.
- Una tarea a la vez; al terminar, dime qué cambiaste para que lo revise.
- Si no estás seguro al 80%, pregunta. No inventes.
- Verifica cada criterio de aceptación de la `spec.md` uno por uno antes de dar la feature por terminada.
- Al cerrar una feature, muévela a "Hecho" en `spec/constitution/roadmap.md`.
- Si `docs/` (material original) contradice a `spec/constitution/` (ya corregido, p. ej. el ORM), manda `spec/constitution/` y avisa de la discrepancia.

## Herramientas del agente (MCP y skills)

- **Skills:** antes de crear/editar archivos o abordar una tarea, **valida la carpeta de skills** (`.claude/skills/`) y revisa si alguna aplica al caso. Si hay una skill relevante, léela y **síguela** en lugar de improvisar. No asumas que no existe una skill sin haber mirado la carpeta primero. (Claude Code usa `.claude/skills/` de forma nativa; OpenCode la lee por compatibilidad, así que sirve para ambos agentes.)
- **Context7 (MCP):** usa el MCP de Context7 para consultar **documentación actualizada** de librerías y frameworks (FastAPI, SQLAlchemy, Alembic, React, etc.) antes de usar una API, en vez de asumirla de memoria. Prioriza lo que devuelva Context7/la skill correspondiente sobre suposiciones.
- **Orden de preferencia:** skill del proyecto aplicable → documentación vía Context7 → conocimiento general. Si algo sigue sin estar claro, pregunta antes de implementar.

## Documentación

- `spec/constitution/mission.md` — qué construimos y para quién
- `spec/constitution/tech-stack.md` — stack, arquitectura, convenciones y límites duros
- `spec/constitution/roadmap.md` — orden de features por sprint
- `spec/features/NNN-nombre/` — `spec.md`, `plan.md` y `tasks.md` de cada feature
- `docs/` — propuesta, análisis, HU, reglas de negocio (RN-01…RN-12), requisitos (RF-01…RF-13), mockups y diagramas
