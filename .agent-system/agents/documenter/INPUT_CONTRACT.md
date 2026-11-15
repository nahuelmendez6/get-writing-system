# Input Contract — Documenter Agent

## 1. Input Sources
The Documenter agent consumes:
1. **`task_spec.md`**: Original specification and technical design.
2. **`implementation_report.md`**: Implementer's delivery notes and modified files list.
3. **`test_report.md`**: Tester's verification results (must have verdict `APPROVED`).
4. **`state/AGENT_HANDOFF.md`**: Incoming handoff payload from Tester.
5. **Existing Documentation**: Markdown files in `/docs`, `.agent-system/knowledge/`, and `CHANGELOG.md`.

## 2. Pre-conditions
- `test_report.md` must have verdict `APPROVED`.
- Task status in `state/CURRENT_TASK.md` must be `IN_DOCUMENTATION`.
