# Changelog — Get Idiomas AI Writing System

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-11-15 (TASK-1.2 - AI-01 / AI-02)
- **AI Service & LangGraph Engine**:
  - Isolated microservice in `/ai_service` built with FastAPI and LangGraph `StateGraph`.
  - Typed state pipeline (`EvaluationState`) with 5 specialized nodes: context preparation, writing analysis, exemplar generation, AI detector, and schema validator.
  - PII masking and anonymization (emails, phone numbers) prior to prompt evaluation.
  - Structured mistake detection for orthography, grammar, punctuation, and lexis with exact character offsets (`start_index`, `end_index`), quotes, and Spanish explanations.
  - Band 5 exemplar rewrite generation preserving candidate arguments while elevating lexical/syntactic cohesion.
  - Synthetic AI text detection with probability score, confidence rating, and "Posible texto generado por IA" alert.
  - Schema validation with conditional self-repair/retry loop (up to 2 retries).
  - Versioned Cambridge prompt guidelines for B2 First and C1 Advanced.
  - Zero Data Retention (ZDR) configuration and containerization in `docker-compose.yml`.
  - Automated test suite with 27 unit/integration tests passing at 94% code coverage and strict typing (`mypy --strict`).
  - Architecture Decision Record: `ADR-002` (LangGraph Evaluation Pipeline & AI Detection).

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
