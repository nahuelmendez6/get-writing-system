---
name: technical-planning
description: Structure comprehensive, testable implementation specifications using the standard task spec template.
---

# Technical Planning Skill

## Purpose
Synthesizes architecture, requirements, and codebase insights into an actionable `task_spec.md`.

## Guidelines
1. **Atomic Scoping**:
   - Keep tasks manageable (implementable within 1-2 days).
   - Divide complex milestones into subtasks (e.g., model & migration first, then service logic, then router).
2. **Acceptance Criteria Crafting**:
   - Write explicit test scenarios in Given-When-Then format covering both happy paths and failure/edge cases.
3. **HITL Gate Evaluation**:
   - Systematically review proposed plans against `workflows/APPROVAL_POLICIES.md` and trigger human approval when required.
