# Output Contract — Documenter Agent

## 1. Deliverables
Upon completing documentation synchronization, the Documenter agent must produce:

1. **Updated Documentation Files**:
   - `CHANGELOG.md` entry.
   - Updated docstrings in modified source code.
   - New or updated ADRs under `docs/adr/` (if architectural decisions occurred).
2. **`documentation_report.md`**:
   - Location: Active task directory.
   - Format: Must conform to `contracts/documentation_report.schema.json`.
3. **State Updates**:
   - `state/CURRENT_TASK.md`: Update status to `IN_COMMITTING`.
   - `state/AGENT_HANDOFF.md`:
     ```yaml
     from_agent: Documenter
     to_agent: Committer
     task_id: [TASK-ID]
     status: SUCCESS
     artifacts:
       - path: [path_to_report]/documentation_report.md
     context_notes: [Summary of documentation updates and commit readiness]
     ```

## 2. Quality & Validation Criteria
- All modified endpoints have updated docstrings and schemas.
- Changelog entry accurately reflects changes under appropriate headings.
