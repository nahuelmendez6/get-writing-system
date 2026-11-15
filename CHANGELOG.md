# Changelog — Get Idiomas AI Writing System

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-11-15 (TASK-1.1 - BE-01 / BE-02)
- **Core Backend Architecture**:
  - FastAPI modular application factory with CORS middleware and structured lifespan manager.
  - Asynchronous SQLAlchemy 2.0 database engine and session management with `asyncpg`.
  - Abstract `BaseModel` providing UUID v4 primary keys (`UUIDPrimaryKeyMixin`) and UTC timezone-aware timestamps (`TimestampMixin`).
  - Structured JSON logging (`JSONFormatter`) with timestamp and sanitized error metadata.
  - Standardized error response handling (`AppException`, `StarletteHTTPException`, `RequestValidationError`, `Exception`) returning canonical `{ "detail": { "error_code", "message", "details" } }` format.
  - Health check endpoints: `GET /health` and `GET /api/v1/health` with active DB ping and degraded-mode resilience.
  - Async database migrations environment initialized with Alembic (`backend/alembic/env.py`).
  - Containerization infrastructure: `backend/Dockerfile` (Python 3.12-slim) and root `docker-compose.yml` (PostgreSQL 16, Redis 7, Backend service on `get_network`).
  - Automated test suite with 12 unit and integration tests passing with 93% code coverage and strict typing (`mypy --strict`).
  - Architecture Decision Record: `ADR-001` (Backend Async Architecture & Model Conventions).
