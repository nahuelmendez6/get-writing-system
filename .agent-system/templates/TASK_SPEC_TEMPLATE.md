# Task Specification: [TASK-ID] — [Task Title]

## 1. Metadata
- **Task ID**: `TASK-X.Y`
- **Backlog Reference**: `[e.g., BE-01, AI-02]`
- **Module / Target Component**: `[/backend, /ai_service, /frontend]`
- **Related Requirements**: `[e.g., RF-01, RF-08, RNF-SEG-01]`
- **Author**: Planner Agent
- **Date**: `YYYY-MM-DD`
- **Status**: `PLANNED`

## 2. Objective & Summary
Brief, concrete explanation of what this task achieves, why it is needed, and how it aligns with the AI-First strategy.

## 3. Technical Analysis & Pre-requisites
- **Existing Codebase Dependencies**: Files/modules that must be inspected or imported.
- **Pre-requisite Tasks**: Other backlog tasks that must be `COMPLETED` before this task can run.
- **Reusable Assets**: Existing models, schemas, or components to leverage.

## 4. Implementation Details

### 4.1. Database Changes (if applicable)
- New tables or column modifications.
- Explicit SQLAlchemy 2.0 model attributes.
- Alembic migration details (`upgrade` and `downgrade` expectations).

### 4.2. API & Data Contracts
- New or modified endpoints (HTTP method, path, status codes).
- Pydantic v2 schemas:
```python
# Request / Response Schemas
```

### 4.3. Business Logic & Service Layer
- Service class and methods to implement.
- LangGraph nodes or edges (if in `ai_service`).
- Error conditions and exceptions to raise.

### 4.4. Frontend Components (if applicable)
- Components to create/update.
- State management and API service hooks.
- Tailwind CSS layout conventions.

## 5. Security, Privacy & Compliance
- **Authentication / RBAC**: Required permissions and ownership verification.
- **GDPR & ZDR**: Data anonymization or privacy requirements.
- **Input Validation**: Field length limits, sanitize rules, regex constraints.

## 6. Acceptance Criteria & Test Scenarios

### Scenario 1: [Happy Path Title]
- **Given**: Initial context / state.
- **When**: Action performed.
- **Then**: Expected outcome.

### Scenario 2: [Error / Edge Case Title]
- **Given**: Initial context.
- **When**: Invalid input or unauthorized request.
- **Then**: Expected HTTP status and error payload.

## 7. Definition of Done Checklist
- [ ] Code follows project architecture & standards.
- [ ] Pydantic / TypeScript contracts strictly typed.
- [ ] Database migration included (if applicable).
- [ ] Unit & integration tests written and passing.
- [ ] No regression introduced.
- [ ] Linting and type checks pass with 0 errors.
