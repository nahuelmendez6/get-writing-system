# Input Contract — Tester Agent

## 1. Input Sources
The Tester agent consumes:
1. **`task_spec.md`**: Approved requirements and acceptance criteria.
2. **`implementation_report.md`**: Implementer's delivery report and list of changed files.
3. **`state/AGENT_HANDOFF.md`**: Incoming handoff payload from Implementer.
4. **Source Code & Test Suites**: Code and tests in `/backend`, `/ai_service`, `/frontend`, and `/tests`.

## 2. Pre-conditions
- `implementation_report.md` must be present and validated against `contracts/implementation_report.schema.json`.
- Task status in `state/CURRENT_TASK.md` must be `IN_TESTING`.
