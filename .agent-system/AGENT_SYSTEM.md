# Agent System

## Project
AI Correction system

## Objective
Implement the project using a coordinated multi-agent
development workflow.

## Agents

1. Planner
2. Implementer
3. Tester
4. Documenter
5. Committer

## Execution Order

Planner
    -> Implementer
    -> Tester
    -> Documenter
    -> Committer

## Correction Loop

If Tester rejects an implementation:

1. Generate a test report.
2. Identify failed requirements.
3. Return the report to Implementer.
4. Implementer fixes the reported problems.
5. Tester executes the validation again.

## Restrictions

- Agents must respect their assigned responsibilities.
- Agents cannot modify architectural decisions without approval.
- Agents must preserve existing functionality.
- Agents must not invent requirements.
- All changes must be traceable to a backlog task.

## Human Approval

Human approval is required for:

- Architectural changes.
- Scope changes.
- Destructive database operations.
- Dependency changes with significant impact.
- Final release approval.
