# GymFlow

Sistema de control de acceso físico y gestión de membresías para gimnasios
pequeños y medianos. Ver `AGENTS.md` para la descripción completa, stack y
convenciones — este README es solo un quickstart.

**Antes de tocar código, lee `AGENTS.md` y `spec/`.** Es un proyecto SDD
(Spec-Driven Development): la fuente de verdad del diseño es `spec/`.

## Estructura

- `backend/` — API FastAPI (monolito modular)
- `frontend/` — kiosko táctil + backoffice (React + Vite + Tailwind)
- `spec/` — constitución + specs de cada feature (SDD)
- `docs/` — material fuente original (propuesta, análisis, diagramas)

## Quickstart local

```bash
cp .env.example .env   # y completar los valores reales

# Backend
cd backend
pipenv install --dev
pipenv run alembic upgrade head
pipenv run uvicorn main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
npm run dev
```

## Con Docker

```bash
cp .env.example .env
docker compose up
```

- Backend: http://localhost:8000 (`/health` para verificar que levantó)
- Frontend: http://localhost:5173
- Postgres: localhost:5432

## Tests

```bash
cd backend
pipenv run pytest
```
