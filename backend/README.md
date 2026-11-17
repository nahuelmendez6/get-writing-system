# Backend — Get Idiomas AI Writing System

Módulo central de backend para la plataforma académica y de evaluación de escritura con IA **Get Idiomas**.

## Requisitos Previos

- Python 3.12+
- Docker y Docker Compose
- PostgreSQL 16 (o servicio dockerizado)
- Redis 7 (o servicio dockerizado)

## Estructura del Módulo

```
backend/
├── app/
│   ├── main.py                  # Fábrica FastAPI, ciclo de vida y middlewares
│   ├── core/                    # Configuración, motor DB, modelos base, excepciones y logs
│   ├── api/v1/                  # Enrutador v1 y endpoints de salud
│   └── schemas/                 # Esquemas de validación Pydantic v2
├── alembic/                     # Migraciones asíncronas de base de datos
├── tests/                       # Pruebas unitarias y de integración
├── Dockerfile                   # Imagen ligera de producción (Python 3.12-slim)
└── pyproject.toml               # Dependencias y configuración de linters
```

## Configuración y Ejecución Local

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
   ```

2. **Variables de entorno:**
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar servidor de desarrollo:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Ejecutar suite de pruebas y cobertura:**
   ```bash
   pytest -v --cov=app
   ```

5. **Verificación de calidad de código:**
   ```bash
   ruff check .
   ruff format --check .
   mypy --strict app tests
   ```

## Endpoints Principales

- `GET /health`: Verificación básica de salud y estado de la base de datos en la raíz.
- `GET /api/v1/health`: Verificación de salud bajo el prefijo API v1.
- `GET /api/v1/rubrics`: Listado de rúbricas con filtrado por nivel CEFR (`?level=B2`) y paginación.
- `GET /api/v1/rubrics/{id}`: Detalle completo de rúbrica con criterios y descriptores de banda.
- `POST /api/v1/rubrics`: Creación de rúbrica con criterios anidados.
- `POST /api/v1/rubrics/{id}/criteria`: Adición de un criterio a una rúbrica existente.
- Documentación interactiva Swagger: `http://localhost:8000/docs`
- Documentación ReDoc: `http://localhost:8000/redoc`
