# Input Contract — Planner Agent

## 1. Input Sources
The Planner agent consumes information from the following canonical files:

1. **Backlog & Requirements**:
   - `backlog`: Phase assignments, task IDs (e.g., `BE-01`, `AI-02`), and priorities.
   - `requirements`: Functional (RF-01 to RF-17) and non-functional requirements.
2. **System Knowledge**:
   - `knowledge/PROJECT_CONTEXT.md`
   - `knowledge/ARCHITECTURE.md`
   - `knowledge/TECHNOLOGY_STACK.md`
   - `knowledge/BUSINESS_RULES.md`
   - `knowledge/SECURITY_RULES.md`
   - `knowledge/CODING_STANDARDS.md`
3. **Current State**:
   - `state/CURRENT_TASK.md`: Current task metadata and phase assignment.
   - `state/EXECUTION_STATUS.md`: Overall backlog status.
   - `state/AGENT_HANDOFF.md`: Incoming handoff payload.
4. **Codebase State**:
   - File system inspection of `/backend`, `/ai_service`, `/frontend`, and existing Alembic migrations.

## 2. Pre-conditions
- The target task in `state/CURRENT_TASK.md` must be in `READY_FOR_PLANNING` or `BACKLOG` state.
- All pre-requisite backlog tasks must be in `COMPLETED` state in `state/EXECUTION_STATUS.md`.
