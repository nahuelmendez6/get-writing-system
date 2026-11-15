# Output Contract — Committer Agent

## 1. Deliverables
Upon executing the git commit, the Committer agent must produce:

1. **Git Commit**:
   - Atomic commit on the active branch with a verified SHA hash.
2. **`commit_report.md`**:
   - Location: Active task directory.
   - Format: Must conform to `contracts/commit_report.schema.json`.
3. **State Finalization**:
   - `state/EXECUTION_STATUS.md`: Mark task status as `COMPLETED`.
   - `state/CURRENT_TASK.md`: Update task status to `DONE` and prepare for subsequent task.
   - `state/AGENT_HANDOFF.md`:
     ```yaml
     from_agent: Committer
     to_agent: Planner
     task_id: [TASK-ID]
     status: COMPLETED
     artifacts:
       - commit_hash: [sha]
       - path: [path_to_report]/commit_report.md
     context_notes: [Task completed and committed. Ready for next backlog task.]
     ```

## 2. Quality & Validation Criteria
- Commit message conforms to Conventional Commits.
- Working directory is clean (`git status` shows no unstaged/untracked files).
