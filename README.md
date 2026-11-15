# Get Idiomas — AI Writing System

Sistema integral de evaluación y corrección asistida por Inteligencia Artificial para exámenes de escritura académica (niveles B1 a C2).

## Arquitectura del Proyecto

El repositorio sigue una arquitectura modular y desacoplada compuesta por:

- `/backend`: API REST académica de alto rendimiento construida con FastAPI, SQLAlchemy 2.0 (asíncrono con PostgreSQL 16) y Alembic.
- `/ai_service`: Motor de evaluación multi-agente orquestado con LangGraph y LLMs multimodales bajo política de Zero Data Retention (ZDR).
- `/frontend`: Aplicación cliente moderna en React 18, TypeScript y Tailwind CSS.

## Despliegue con Docker Compose

Para levantar el entorno completo de desarrollo (PostgreSQL 16, Redis 7 y Backend):

```bash
# 1. Copiar configuración de variables de entorno
cp .env.example .env

# 2. Iniciar los contenedores
docker-compose up -d --build

# 3. Comprobar salud del backend
curl http://localhost:8000/health
```

## Calidad y Pruebas del Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"

# Ejecución de tests y cobertura
pytest -v --cov=app

# Verificaciones estáticas
ruff check .
ruff format --check .
mypy --strict app tests
```

## Documentación Técnica

- [Decisiones de Arquitectura (ADRs)](docs/adr/)
- [Requisitos Funcionales y No Funcionales](docs/requirements/functional-and-non-functional-requirements.md)
- [Backlog General](docs/backlog/backlog.md)
- [Registro de Cambios (Changelog)](CHANGELOG.md)
