# Input Contract — Implementer Agent

## 1. Input Sources
The Implementer agent consumes:
1. **`task_spec.md`**: The approved technical specification produced by the Planner agent.
2. **`state/AGENT_HANDOFF.md`**: Incoming handoff payload from Planner (or Tester during a revision loop).
3. **`knowledge/` Base**: Coding standards, security rules, and architectural guidelines.
4. **Existing Codebase**: Current code in `/backend`, `/ai_service`, and `/frontend`.
5. **`test_report.md`** *(only during Rejection Loop)*: Failure analysis and required remediations from Tester.

## 2. Pre-conditions
- `task_spec.md` must be present and validated against `contracts/task_spec.schema.json`.
- Task status in `state/CURRENT_TASK.md` must be `PLANNED` or `REVISION_REQUIRED`.
