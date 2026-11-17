# Changelog — Get Idiomas AI Writing System

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2026-11-17 (TASK-2.1 - QA-01 / AI-04 Lite)
- **Multimodal OCR & Literal Transcription Engine (`AI-04 Lite`)**:
  - Image processing module `image_processing.py` with EXIF metadata stripping (purging GPS, device, and timestamps for GDPR compliance on minor submissions) and format normalization (JPEG, PNG, WEBP).
  - LangGraph node `ocr_transcription_node` enforcing the **Literal OCR Principle**: strictly preserves all spelling, grammatical, punctuation, and structural errors made by the student without autocorrecting.
  - Evaluation pipeline extended to 8 nodes in `StateGraph` accepting Base64 images or digital text, tracking `ocr_applied`, `ocr_confidence`, and `extracted_text`.
- **Benchmark & Testing Harness (`QA-01`)**:
  - Mathematical metrics engine `metrics.py` computing Mean Absolute Error (MAE), MSE, exact band match rate, and $\pm 1$ band concordance.
  - Interactive CLI console runner (`ai_service/app/benchmark/cli.py` & `ai_service/scripts/run_benchmark.py`) for evaluating single handwritten images or running batch benchmarks with rich terminal display and exports.
  - Calibrated benchmark dataset (`ai_service/data/benchmark/dataset.json`) with 60 representative writing samples across B1, B2, C1, C2 and all 7 task genres (Essay, Article, Email, Review, Report, Story, Proposal) with teacher ground-truth scores.
  - Benchmark empirical results achieving $\text{MAE} = 0.306$ bands (exceeding target $\le 0.50$) and $99.6\%$ concordance in $\pm 1$ band (exceeding target $\ge 80.0\%$).
  - Architecture Decision Record: `ADR-004` (Multimodal Literal OCR & Benchmark Validation Harness).
  - Test suite extended to 70 total tests passing at 86.5% global code coverage (92% backend, 81% ai_service) with strict typing (`mypy --strict`).

### Added - 2026-11-17 (TASK-1.3 - AI-03 / BE-06)
- **Reusable Rubrics Module (`BE-06`)**:
  - SQLAlchemy 2.0 declarative models `Rubric` and `RubricCriterion` with UUID v4 primary keys, UTC timestamps, JSONB descriptors, and cascade deletes.
  - Reversible Alembic migration `001_create_rubrics_and_criteria.py` for `rubrics` and `rubric_criteria` tables.
  - RESTful endpoints under `/api/v1/rubrics`: list with CEFR level filter and pagination, get by ID, create rubric, and add criteria.
  - Default Cambridge B2 First and C1 Advanced seed templates with complete official descriptors for *Content*, *Communicative Achievement*, *Organisation*, and *Language* across Bands 0 to 5.
  - Deterministic institutional score calculation mapping raw score (0-20) to decimal grade (0.0-10.0) without exposing registered trademarks.
  - Synchronized OpenAPI definition at `backend/openapi.json`.
- **AI Service Rubric Evaluation & Feedback Engine (`AI-03`)**:
  - New LangGraph node `rubric_eval` evaluating Cambridge 4-band criteria (0-5 scale) with textual justifications and word length tolerance checking ($\pm 10\%$).
  - New LangGraph node `feedback_gen` generating structured Spanish pedagogical feedback: overall summary, 2-4 strengths, 2-4 areas for improvement, and exactly 3 actionable tips.
  - Pipeline extension to 7 nodes in `StateGraph` with typed state preservation (`EvaluationState`) and enhanced validator checks (`validator_node`).
  - Response contract update in `EvaluationResponse` with `rubric_evaluation` and `feedback` schemas.
  - Synchronized OpenAPI definition at `ai_service/openapi.json`.
  - Architecture Decision Record: `ADR-003` (Cambridge Rubrics & Pedagogical Scoring Engine).
  - 56 total automated unit and integration tests passing at 93.3% global code coverage (92% backend, 94% ai_service) with strict typing (`mypy --strict`).

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
