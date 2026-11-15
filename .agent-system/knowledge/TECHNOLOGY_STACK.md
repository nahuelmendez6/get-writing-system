# Technology Stack — Get Idiomas AI Writing System

## 1. Core Architecture Overview

```
                      +-----------------------------+
                      |       Frontend Client       |
                      |   React 18 + TypeScript     |
                      |       Tailwind CSS          |
                      +--------------+--------------+
                                     | HTTPS / REST
                                     v
                      +-----------------------------+
                      |       FastAPI Backend       |
                      |       Python 3.12+          |
                      |      SQLAlchemy 2.x         |
                      +-------+-------------+-------+
                              |             |
           +------------------+             +------------------+
           | Internal REST / Task                              | Async Tasks
           v                                                   v
+-----------------------+                             +-----------------+
|   AI Service Engine   |                             |  Redis 7 Broker |
|   LangGraph Pipeline  |                             |   & Celery 5    |
|   Multimodal LLMs     |                             +--------+--------+
+-----------------------+                                      |
                                                               v
+--------------------------------------------------------------+--------+
|                      Infrastructure Layer                             |
|  PostgreSQL 16 (Relational DB)  |  S3 / MinIO (Object Storage)        |
+-----------------------------------------------------------------------+
```

## 2. Backend Stack

- **Runtime & Language**: Python 3.12+
- **API Framework**: FastAPI (high performance ASGI framework)
- **Data Validation & Settings**: Pydantic v2 and `pydantic-settings`
- **Database ORM**: SQLAlchemy 2.0 (Modern declarative mapped models)
- **Database Migrations**: Alembic
- **Relational Database**: PostgreSQL 16
- **Asynchronous Task Queue**: Celery 5.x with Redis 7 as broker and result backend
- **Authentication & Security**:
  - `python-jose` / `pyjwt` for JWT access and refresh token management.
  - `passlib[argon2]` or `bcrypt` for cryptographic password hashing.
- **Object Storage Client**: `boto3` / `aioboto3` for MinIO/S3 compatible storage and pre-signed upload/download URLs.

## 3. AI Service Stack (`ai_service`)

- **Language & Environment**: Python 3.12+ (isolated service container)
- **Graph Orchestration**: LangGraph (StateGraph pipeline for sequential and conditional evaluation nodes)
- **LLM Integrations**:
  - Multimodal Vision-Language Models (e.g., GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro) with **Zero Data Retention (ZDR)** enforced.
- **Output Structuring**: Pydantic v2 schemas enforcing strict JSON output validation with retry logic.
- **Image Preprocessing**: Pillow (`PIL`) and OpenCV for EXIF metadata sanitization, image orientation correction, and contrast normalization for OCR.

## 4. Frontend Stack (`frontend`)

- **Core Library**: React 18+ with TypeScript 5+ (Strict mode enabled)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with PostCSS
- **Iconography**: Lucide React
- **State Management & Data Fetching**: React Context API + Custom Hooks with Axios / Fetch API interceptors for automatic token refresh.
- **UI Components**:
  - `VirtualWritingEditor`: Word counter, localStorage auto-save, and exam lock.
  - `CorrectionInterfacePage`: Dual-column canvas with `InteractiveTextAnnotator`, `RubricScoreSliders`, and OCR Split View modal.

## 5. Storage & Infrastructure

- **Primary Database**: PostgreSQL 16
  - UUID primary keys for all business entities.
  - UTC timestamps (`created_at`, `updated_at`).
  - Strict foreign key constraints with indexed lookup fields.
- **Object Storage**: MinIO (local development) and AWS S3 / Hetzner Object Storage (production).
  - Private buckets with restricted pre-signed URL access (15-30 min expiration).
- **Containerization**: Multi-stage Dockerfiles and `docker-compose.yml` for unified development orchestration.

## 6. Testing & Quality Tooling

- **Backend Testing**:
  - `pytest` with `pytest-asyncio`.
  - `httpx` for ASGI asynchronous API testing (`AsyncClient`).
  - `factory-boy` or custom fixtures for database seeding.
- **Frontend Testing**:
  - `vitest` and `@testing-library/react`.
- **Code Quality & Linting**:
  - Python: `ruff` (linter and formatter), `mypy` (strict type checks).
  - TypeScript: `eslint`, `prettier`, and `tsc --noEmit`.
