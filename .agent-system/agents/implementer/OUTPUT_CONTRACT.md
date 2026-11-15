# Output Contract — Implementer Agent

## 1. Deliverables
Upon completing code authoring, the Implementer agent must produce:

1. **Source Code**:
   - Application code committed in working tree across target directories (`/backend`, `/ai_service`, `/frontend`).
   - Alembic migration scripts (if database models changed).
   - Unit and integration test files under `/tests`.
2. **`implementation_report.md`**:
   - Location: Active task directory.
   - Format: Must conform to `templates/IMPLEMENTATION_REPORT_TEMPLATE.md`.
   - Schema Validation: Must validate against `contracts/implementation_report.schema.json`.
3. **State Updates**:
   - `state/CURRENT_TASK.md`: Update status to `IN_TESTING`.
   - `state/AGENT_HANDOFF.md`:
     ```yaml
     from_agent: Implementer
     to_agent: Tester
     task_id: [TASK-ID]
     status: SUCCESS
     artifacts:
       - path: [path_to_report]/implementation_report.md
     context_notes: [Summary of changes and testing instructions]
     ```

## 2. Quality & Validation Criteria
- `ruff check .` and `mypy` pass with 0 errors.
- All new tests pass locally.
- Reversible migrations verified with `upgrade` and `downgrade`.
