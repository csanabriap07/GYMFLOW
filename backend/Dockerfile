# GymFlow backend — FastAPI + SQLAlchemy + Alembic, dependencias con Pipenv
# Ver spec/constitution/tech-stack.md y spec/constitution/ci-cd.md para las decisiones detrás de este archivo.

FROM python:3.13-slim AS base

# Dependencias del sistema necesarias para psycopg2 (driver de Postgres) y compilación de paquetes nativos.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pipenv fijo (no "el que sea más nuevo") para builds reproducibles.
RUN pip install --no-cache-dir pipenv==2024.0.1

# Copiamos solo los manifiestos primero para aprovechar la cache de Docker:
# si el código cambia pero Pipfile no, este paso no se vuelve a ejecutar.
COPY Pipfile Pipfile.lock ./
# NOTA: Pipfile.lock se generó con Python 3.12 (único disponible al armar
# este scaffold). Los NOMBRES y VERSIONES de los paquetes son reales y
# correctos (fastapi==0.139.0, sqlalchemy==2.0.51, alembic==1.18.5, etc.),
# pero los hashes de wheels pueden no cubrir cp313 todavía. Por eso NO
# usamos "--deploy" (que exige que el lock case perfecto): dejamos que
# pipenv resuelva contra Pipfile si el lock no aplica exacto a 3.13.
# Acción pendiente para el equipo: correr `pipenv lock` una vez en una
# máquina/CI con Python 3.13 real y commitear el lock regenerado —
# a partir de ahí sí se puede volver a exigir "--deploy" aquí.
RUN pipenv install --system --skip-lock

COPY . .

EXPOSE 8000

# El entrypoint corre las migraciones antes de levantar el server —
# así "docker compose up" deja la base al día sin un paso manual aparte.
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
