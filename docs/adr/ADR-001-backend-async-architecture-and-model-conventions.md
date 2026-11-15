# Architecture Decision Record (ADR): ADR-001 Backend Async Architecture & Model Conventions

## 1. Metadata
- **Status**: `Accepted`
- **Date**: `2026-11-15`
- **Authors**: `Documenter Agent / System Architect`
- **Related Task**: `TASK-1.1`
- **Supercedes / Superceded by**: `N/A`

## 2. Context & Problem Statement
El sistema académico **Get Idiomas AI Writing System** requiere una infraestructura backend de alto rendimiento capaz de manejar consultas concurrentes, persistencia relacional estricta, integración desacoplada con el motor de IA (`ai_service`) y tareas asíncronas de fondo (Celery/Redis).
Asimismo, se requiere garantizar la inmutabilidad, trazabilidad y consistencia de los identificadores y marcas temporales en todas las entidades del dominio antes de iniciar el modelado de rúbricas, usuarios y entregas.

## 3. Decision Drivers
- Rendimiento y alta concurrencia mediante operaciones I/O no bloqueantes (FastAPI + SQLAlchemy 2.0 asíncrono con `asyncpg`).
- Desacoplamiento arquitectónico entre la capa de entrega (HTTP / Routers), servicios y persistencia.
- Unicidad global y seguridad contra enumeración de IDs primarios (prevención de fugas de datos de estudiantes).
- Consistencia temporal absoluta en evaluaciones, revisiones y envíos mediante marcas temporales UTC timezone-aware.
- Reproducibilidad de entornos de desarrollo y producción mediante Docker y migraciones versionadas con Alembic.

## 4. Considered Options
1. **Opción A (Sincrónica tradicional)**: FastAPI o Flask con SQLAlchemy 1.4 sincrónico y psycopg2.
2. **Opción B (Asíncrona modular con UUID v4)**: FastAPI con SQLAlchemy 2.0 (`asyncpg`), `BaseModel` abstracto unificado con UUID v4 y UTC `created_at`/`updated_at`, Alembic asíncrono y Docker Compose.
3. **Opción C (NoSQL / Documental puro)**: MongoDB o Firestore.

## 5. Decision Outcome
Opción elegida: **Opción B**, debido a que cumple estrictamente con los requerimientos funcionales (`RF-01`, `RF-02`) y no funcionales (`RNF-REND-01`, `RNF-SEG-01`), preservando la integridad referencial relacional de PostgreSQL a la vez que maximiza el rendimiento ASGI no bloqueante.

### 5.1. Consecuencias Positivas
- Identificadores UUID v4 opacos previenen ataques de enumeración y colisiones distribuidas.
- Todas las marcas de tiempo se almacenan estandarizadas en UTC con información de zona horaria (`DateTime(timezone=True)`).
- Esquemas de migración automáticos y testeables de forma asíncrona mediante `alembic check` y scripts versionados.
- Respuestas de error canónicas y sanitizadas para prevenir exposición de detalles internos de la base de datos.

### 5.2. Consecuencias Negativas y Mitigaciones
- Mayor complejidad sintáctica con `await session.execute(...)` y `asyncpg` en comparación con ORM sincrónico.
  - *Mitigación*: Se provee `get_db_session` como dependencia estándar inyectable y fixtures de pruebas asíncronas probadas en pytest.

## 6. Implementation Notes & Guidelines
- Todas las entidades de base de datos futuras deben heredar de `app.core.models.BaseModel`.
- Jamás utilizar identificadores autoincrementales enteros secuenciales como clave primaria expuesta al cliente.
- Las sesiones de base de datos deben consumirse exclusivamente mediante `Depends(get_db_session)`.
