# Task Specification: TASK-1.1 — Core Backend: Configuración de FastAPI, PostgreSQL, Alembic y Docker

## 1. Metadata
- **Task ID**: `TASK-1.1`
- **Backlog Reference**: `BE-01 / BE-02`
- **Module / Target Component**: `/backend`
- **Related Requirements**: `RF-01`, `RF-02`, `RNF-REND-01`, `RNF-SEG-01`
- **Author**: Planner Agent
- **Date**: `2026-11-13`
- **Status**: `COMPLETED`

---

## 2. Objective & Summary
Establecer la infraestructura de base del backend académico para el sistema **Get Idiomas AI Writing System**. Esta tarea proporciona el andamiaje técnico, arquitectura en capas, conexión asíncrona a base de datos PostgreSQL, soporte de migraciones automatizadas con Alembic, convenciones uniformes de modelos ORM (identificadores UUID v4 y marcas de tiempo UTC), contenedorización reproducible con Docker y Docker Compose, y endpoints de salud de sistema con verificación de conectividad a la base de datos.

Esta base es el prerrequisito indispensable de la estrategia **AI-First**, permitiendo que las tareas subsiguientes (`TASK-1.2` ai_service y `TASK-1.3` evaluación/rúbricas) dispongan de contratos limpios, persistencia desacoplada y entorno dockerizado para pruebas y benchmarks masivos.

---

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**: 
  - La raíz del proyecto cuenta con directorios vacíos `/backend`, `/ai_service` y `/frontend`.
  - Esta tarea crea la estructura de código fundacional en `/backend` y archivos de despliegue en raíz (`docker-compose.yml`, `.env.example`).
- **Pre-requisite Tasks**: Ninguna (Tarea inicial de la Fase 1).
- **Reusable Assets**:
  - Especificaciones de arquitectura definidas en `.agent-system/knowledge/ARCHITECTURE.md`.
  - Estándares de codificación de `.agent-system/knowledge/CODING_STANDARDS.md`.
  - Pila tecnológica de `.agent-system/knowledge/TECHNOLOGY_STACK.md`.

---

## 4. Implementation Details

### 4.1. Project Layout & Dependencies
El directorio `backend/` implementará la arquitectura modular por dominios:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Fábrica FastAPI, middlewares CORS, ciclo de vida (lifespan)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings con pydantic-settings
│   │   ├── database.py          # AsyncEngine, async_sessionmaker, get_db_session
│   │   ├── models.py            # Declarative Base y BaseModelMixin (UUID, timestamps)
│   │   ├── exceptions.py        # Excepciones custom y manejadores estandarizados
│   │   └── logging.py           # Logging estructurado JSON
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Agregador de rutas v1
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── health.py    # GET /health y GET /api/v1/health
│   └── schemas/
│       ├── __init__.py
│       └── health.py            # Pydantic schema de estado de salud
├── alembic/
│   ├── env.py                   # Configuración asíncrona de migraciones
│   ├── script.py.mako           # Plantilla de generación de migraciones
│   └── versions/                # Directorio de versiones de migraciones
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest asíncronos y BD en memoria
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_models.py       # Pruebas unitarias de modelos base y UUID/UTC
│   └── integration/
│       ├── __init__.py
│       └── test_health.py       # Pruebas de endpoints /health y degradación
├── alembic.ini                  # Configuración raíz de Alembic
├── Dockerfile                   # Imagen ligera Python 3.12-slim
├── pyproject.toml / requirements.txt # Dependencias del backend
└── .env.example                 # Variables de entorno de desarrollo
```

### 4.2. Database Changes & Model Conventions
- **ORM**: SQLAlchemy 2.0 con soporte asíncrono (`asyncpg`).
- **Base Declarativa y Mixin**:
  Todas las entidades del sistema heredarán de un `BaseModelMixin` o `BaseModel` común que garantiza consistencia:
  ```python
  import uuid
  from datetime import datetime, timezone
  from sqlalchemy import DateTime
  from sqlalchemy.dialects.postgresql import UUID
  from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

  class Base(DeclarativeBase):
      pass

  class TimestampMixin:
      created_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True),
          default=lambda: datetime.now(timezone.utc),
          nullable=False
      )
      updated_at: Mapped[datetime] = mapped_column(
          DateTime(timezone=True),
          default=lambda: datetime.now(timezone.utc),
          onupdate=lambda: datetime.now(timezone.utc),
          nullable=False
      )

  class UUIDPrimaryKeyMixin:
      id: Mapped[uuid.UUID] = mapped_column(
          UUID(as_uuid=True),
          primary_key=True,
          default=uuid.uuid4,
          nullable=False
      )

  class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
      __abstract__ = True
  ```
- **Gestión de Sesión Asíncrona**:
  ```python
  from collections.abc import AsyncGenerator
  from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

  engine = create_async_engine(settings.DATABASE_URL, echo=settings.DB_ECHO, future=True)
  AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

  async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
      async with AsyncSessionLocal() as session:
          try:
              yield session
          finally:
              await session.close()
  ```
- **Alembic**:
  - `alembic/env.py` configurado con soporte asíncrono (`run_async_migrations` o conexión sincrónica wrapper).
  - Enlaza `target_metadata = Base.metadata`.
  - Generación del directorio inicial de migraciones sin tablas iniciales (las tablas de negocio se agregarán en sus tareas correspondientes).

### 4.3. API & Data Contracts
- **Endpoints**:
  - `GET /health` y `GET /api/v1/health`
  - Método: `GET`
  - Código HTTP esperado: `200 OK` (o `503 SERVICE UNAVAILABLE` si la verificación crítica falla).
  - Contrato Pydantic:
  ```python
  from datetime import datetime
  from pydantic import BaseModel, ConfigDict, Field

  class HealthCheckResponse(BaseModel):
      model_config = ConfigDict(from_attributes=True)

      status: str = Field(..., description="Estado general del servicio ('healthy', 'degraded')")
      environment: str = Field(..., description="Entorno de ejecución ('development', 'staging', 'production')")
      version: str = Field(..., description="Versión del backend")
      database: str = Field(..., description="Estado de conectividad con la BD ('connected', 'disconnected')")
      timestamp: datetime = Field(..., description="Marca temporal UTC de la verificación")

  class ErrorDetail(BaseModel):
      error_code: str = Field(..., description="Código de error canónico")
      message: str = Field(..., description="Mensaje explicativo para el cliente")
      details: dict = Field(default_factory=dict, description="Metadatos adicionales del fallo")

  class StandardErrorResponse(BaseModel):
      detail: ErrorDetail
  ```

### 4.4. Business Logic & Service Layer
- **Health Service**:
  - Consulta a la base de datos ejecutando `SELECT 1` mediante `await session.execute(text("SELECT 1"))`.
  - En caso de fallo o timeout de conexión con la base de datos, captura la excepción de forma controlada y establece `database: "disconnected"`, asignando `status: "degraded"`.
- **Manejo Global de Excepciones**:
  - Middleware / exception handlers para `HTTPException`, `RequestValidationError` y `Exception` no capturadas.
  - Formato uniforme de error:
    ```json
    {
      "detail": {
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "Ha ocurrido un error inesperado.",
        "details": {}
      }
    }
    ```

### 4.5. Frontend Components
- N/A para esta tarea (infraestructura exclusiva de backend).

### 4.6. Infrastructure & Containerization
- **Dockerfile** (`backend/Dockerfile`):
  - Base: `python:3.12-slim`.
  - Instalación de librerías de sistema necesarias (ej. `gcc`, `libpq-dev`).
  - Instalación de dependencias de Python sin cache.
  - Puerto expuesto: `8000`.
  - Entrypoint: `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- **Docker Compose** (`docker-compose.yml` en la raíz):
  - Servicio `postgres`: Imagen `postgres:16-alpine`, puertos `5432:5432`, variables de entorno para DB, usuario, password; healthcheck con `pg_isready`.
  - Servicio `redis`: Imagen `redis:7-alpine`, puertos `6379:6379`, healthcheck con `redis-cli ping`.
  - Servicio `backend`: Build desde `./backend`, volumen para hot-reload `./backend:/app`, variables de entorno conectando a postgres y redis.
  - Red común: `get_network`.

---

## 5. Security, Privacy & Compliance
- **Configuración de Variables de Entorno**:
  - Contraseñas y cadenas de conexión a base de datos deben configurarse mediante variables de entorno (`.env`), documentadas con valores de ejemplo seguros en `.env.example`.
- **Sanitización de Respuestas de Error**:
  - Se prohíbe exponer trazas internas de la base de datos (`Internal Server Error` genérico sin revelar nombres de tablas, usuarios o contraseñas).
- **Protección CORS**:
  - Middlewares de CORS restringidos a orígenes permitidos configurables vía variable de entorno `ALLOWED_ORIGINS`.
- **Cumplimiento RF-01 / RF-02**:
  - El sistema base no habilita endpoints de autenticación inseguros ni conmutadores de rol de prueba en modo producción.

---

## 6. Acceptance Criteria & Test Scenarios

### Scenario 1: Verificación de salud del sistema (Happy Path)
- **Given**: La aplicación FastAPI y la base de datos se encuentran inicializadas y operativas.
- **When**: Se envía una petición `GET /health` o `GET /api/v1/health`.
- **Then**: El sistema responde con status HTTP 200 OK y un cuerpo JSON con:
  - `status`: `"healthy"`
  - `database`: `"connected"`
  - `environment`: valor configurado (ej. `"development"`)
  - `version`: valor semántico (ej. `"0.1.0"`)
  - `timestamp`: marca temporal UTC válida.

### Scenario 2: Resiliencia ante desconexión de base de datos (Degraded Mode)
- **Given**: La aplicación FastAPI está corriendo pero la base de datos PostgreSQL no responde o está apagada.
- **When**: Se envía una petición `GET /health` o `GET /api/v1/health`.
- **Then**: El sistema maneja la excepción internamente sin provocar un crash del proceso y responde con status `status`: `"degraded"`, `database`: `"disconnected"`.

### Scenario 3: Convención estricta de Modelos ORM (UUID y UTC)
- **Given**: Una entidad de prueba que hereda de `BaseModel`.
- **When**: Se instancia una nueva fila de dicha entidad y se valida su configuración.
- **Then**: El campo `id` es un UUID versión 4, y los campos `created_at` y `updated_at` contienen datetimes conscientes de zona horaria (UTC timezone-aware).

### Scenario 4: Inicialización del entorno de migraciones Alembic
- **Given**: El archivo `alembic.ini` y el directorio `alembic/` configurados con soporte asíncrono.
- **When**: Se ejecuta `alembic check` o se importa `alembic.env`.
- **Then**: Se enlaza exitosamente con `Base.metadata` y se prepara para recibir futuras migraciones de esquemas sin errores de sintaxis.

---

## 7. Definition of Done Checklist
- [ ] Código del backend sigue la arquitectura modular por capas definida en `CODING_STANDARDS.md`.
- [ ] Modelos base SQLAlchemy 2.0 y esquemas Pydantic v2 estrictamente tipados.
- [ ] Entorno de migraciones Alembic configurado y operativo.
- [ ] Endpoints de verificación de salud (`/health` y `/api/v1/health`) implementados.
- [ ] `Dockerfile` y `docker-compose.yml` listos para levantar PostgreSQL 16 y Redis 7.
- [ ] Pruebas unitarias y de integración pasando con 100% de éxito.
- [ ] `ruff check` y `mypy --strict` pasando sin errores.
