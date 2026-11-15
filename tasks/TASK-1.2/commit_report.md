# Commit Report: TASK-1.2 — Servicio de IA y Grafo (ai_service con LangGraph)

## 1. Metadata
- **Task ID**: `TASK-1.2`
- **Committer**: Committer Agent
- **Date**: `2026-11-15`
- **Related Task**: `TASK-1.2` (Backlog: `AI-01 / AI-02`)
- **Status**: `COMPLETED`

## 2. Commit Information
- **Commit Type**: `feat`
- **Scope**: `ai_service`
- **Commit Hash**: `3339a773777ee30bdd3f30e2409a6e9f1e15980f`
- **Header**: `feat(ai_service): implement langgraph evaluation pipeline, writing analysis and ai detection`
- **Body**:
  ```
  - Create isolated FastAPI microservice ai_service with Dockerfile and compose setup
  - Implement LangGraph StateGraph pipeline with typed EvaluationState
  - Add context_prep_node with PII sanitization and word counting
  - Add writing_analysis_node detecting grammar, spelling and lexis mistakes with character offsets
  - Add exemplar_gen_node generating Band 5 exemplary rewritten texts
  - Add ai_detector_node detecting synthetic AI text patterns with probability alerts
  - Add validator_node with conditional self-repair/retry loop
  - Add Cambridge B2 First and C1 Advanced prompt guidelines
  - Enforce Zero Data Retention (ZDR) configuration
  - Add ADR-002, OpenAPI schema sync, and 27 automated unit/integration tests with 94% coverage

  Task-Ref: TASK-1.2
  ```

## 3. Verification & Compliance
- [x] All 27 unit and integration tests passed with 94% coverage.
- [x] Backend regression tests verified: 12/12 passing.
- [x] `mypy --strict` and `ruff check` passed cleanly in all files.
- [x] Conventional Commits standard adhered to.
- [x] State updated: `CURRENT_TASK.md` marked as `COMPLETED`.
