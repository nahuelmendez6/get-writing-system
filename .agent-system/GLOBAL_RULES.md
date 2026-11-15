# Global Rules for Autonomous Agent System

These rules are non-negotiable and apply to all agents (Planner, Implementer, Tester, Documenter, Committer) at all times.

## 1. Traceability & Scope
1. **Backlog Integrity**: Every action, file modification, and commit must correspond to an explicit task in `backlog` and respect the functional requirements in `requirements`.
2. **Zero Scope Creep**: Agents must never introduce speculative features, unofficial abstractions, or unrequested endpoints.
3. **Specification First**: No code implementation can start without an approved `task_spec.md` created by the Planner agent.

## 2. Architectural Boundaries
1. **Decoupled AI Engine**: The `ai_service` (LangGraph) must remain completely decoupled from the academic `backend` (FastAPI). The frontend must NEVER call `ai_service` or LLM providers directly.
2. **Explicit Contracts**: All communication between `backend` and `ai_service` must use strict Pydantic schemas defined in contracts.
3. **Asynchronous Processing**: Heavy AI workloads and OCR transcriptions must be executed asynchronously via Celery and Redis workers.
4. **Data Isolation & Immutability**:
   - `AIEvaluation` records are strictly immutable once generated.
   - `TeacherReview` is mutable and represents official feedback published to students.
   - Students must NEVER be able to query drafts or pending AI evaluations.

## 3. Security, Privacy & Compliance (GDPR)
1. **Zero Data Retention (ZDR)**: All LLM API calls must enforce ZDR policies (no training on user submissions).
2. **Anonymization**: Submissions must have student PII (names, emails, IDs) stripped before being forwarded to any external AI provider.
3. **No DNI as Password**: In compliance with RF-01 and privacy guidelines, DNI must never be used as an access credential or plaintext password. Secure email/password authentication with bcrypt/Argon2 hashing and JWT with short-lived tokens is mandatory.
4. **Production Safeguards**: Role switches (e.g., `DevRoleSwitcher`) and 1-click demo logins must be completely stripped or strictly disabled in production environments (`ENVIRONMENT=production`).
5. **Least Privilege (RBAC)**: Enforce role-based access control (ADMIN, TEACHER, STUDENT) combined with object-level ownership checks (e.g., a teacher only manages assigned courses; a student only accesses own submissions).

## 4. Evaluation & Domain Logic
1. **Cambridge Framework Alignment**: Criterions follow standard Cambridge scales (Content, Communicative Achievement, Organisation, Language) evaluated on 0-5 band scales.
2. **Internal Scoring**: Conversion to a 10-point scale must use an internal mathematical formula without using the proprietary "Cambridge" trademark on student reports.
3. **Literal OCR Principle**: Handwriting OCR transcription must be strictly literal, preserving orthographic, punctuation, and structural errors made by the student without auto-correcting them during transcription.
4. **Band 5 Model Visibility**: The exemplary Band 5 text visibility must respect assignment configuration (e.g., visible only after 2nd version resubmission).

## 5. Development & Code Quality
1. **Strict Typing**: Python 3.12+ type hints and TypeScript strict mode must be strictly maintained. No `Any` without explicit justification.
2. **Database Migrations**: Every schema change requires an accompanying Alembic migration script with both `upgrade()` and `downgrade()` steps.
3. **Atomic Execution**: Changes must be made in atomic, cohesive units. Never leave the repository in a broken state.
4. **Definition of Done**: A task is only complete when all DoD criteria in `DEFINITION_OF_DONE.md` are fulfilled and validated by the Tester agent.
5. **Git Hygiene**: Commits must follow the Conventional Commits specification and be authored exclusively by the Committer agent after test approval.
