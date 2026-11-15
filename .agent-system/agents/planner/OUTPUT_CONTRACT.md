# Output Contract — Planner Agent

## 1. Deliverables
Upon completing a planning cycle, the Planner agent must produce:

1. **`task_spec.md`**:
   - Location: `tasks/[TASK-ID]/task_spec.md` (or embedded in active task context).
   - Format: Must conform to `templates/TASK_SPEC_TEMPLATE.md`.
   - Schema Validation: Must validate against `contracts/task_spec.schema.json`.
2. **State Updates**:
   - `state/CURRENT_TASK.md`: Update state to `PLANNED` (or `WAITING_HUMAN_APPROVAL` if gates triggered).
   - `state/AGENT_HANDOFF.md`:
     ```yaml
     from_agent: Planner
     to_agent: Implementer
     task_id: [TASK-ID]
     status: SUCCESS
     artifacts:
       - path: tasks/[TASK-ID]/task_spec.md
     context_notes: [Technical overview for Implementer]
     ```

## 2. Quality & Validation Criteria
- Every planned endpoint must specify HTTP method, path, status codes, and Pydantic schemas.
- If database modifications are required, specify table names, column types, and migration necessity.
- Every task specification must contain at least 2 concrete Given-When-Then test scenarios.
