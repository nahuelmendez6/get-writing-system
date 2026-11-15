# Input Contract — Committer Agent

## 1. Input Sources
The Committer agent consumes:
1. **`task_spec.md`**: Context of the completed task.
2. **`test_report.md`**: Approved verification report from the Tester.
3. **`documentation_report.md`**: Documentation synchronization confirmation from Documenter.
4. **`state/AGENT_HANDOFF.md`**: Incoming handoff payload from Documenter.
5. **Git Repository Status**: `git status` and `git diff` output.

## 2. Pre-conditions
- `test_report.md` must have verdict `APPROVED`.
- `documentation_report.md` must have status `COMPLETED`.
- Task status in `state/CURRENT_TASK.md` must be `IN_COMMITTING`.
