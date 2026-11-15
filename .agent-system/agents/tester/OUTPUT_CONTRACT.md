# Output Contract — Tester Agent

## 1. Deliverables
Upon completing test verification, the Tester agent must produce:

1. **`test_report.md`**:
   - Location: Active task directory.
   - Format: Must conform to `templates/TEST_REPORT_TEMPLATE.md`.
   - Schema Validation: Must validate against `contracts/test_report.schema.json`.
2. **State Updates**:
   - **If APPROVED**:
     - `state/CURRENT_TASK.md`: Update status to `IN_DOCUMENTATION`.
     - `state/AGENT_HANDOFF.md`:
       ```yaml
       from_agent: Tester
       to_agent: Documenter
       task_id: [TASK-ID]
       status: SUCCESS
       artifacts:
         - path: [path_to_report]/test_report.md
       context_notes: [Test summary and approval confirmation]
       ```
   - **If REJECTED**:
     - `state/CURRENT_TASK.md`: Update status to `REVISION_REQUIRED`.
     - `state/AGENT_HANDOFF.md`:
       ```yaml
       from_agent: Tester
       to_agent: Implementer
       task_id: [TASK-ID]
       status: FAILURE
       artifacts:
         - path: [path_to_report]/test_report.md
       context_notes: [Defect analysis and required remediation instructions]
       ```

## 2. Quality & Validation Criteria
- Contains exact test metrics (passed, failed, duration, coverage).
- Every failing test has a corresponding defect entry with root cause analysis.
