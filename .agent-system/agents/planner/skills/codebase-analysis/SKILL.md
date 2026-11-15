---
name: codebase-analysis
description: Inspect and analyze the existing repository structure, files, dependencies, and database schemas.
---

# Codebase Analysis Skill

## Purpose
Ensures technical plans build upon verified codebase facts rather than speculative assumptions.

## Guidelines
1. **Repository Inspection**:
   - Check existing module layouts under `/backend`, `/ai_service`, and `/frontend`.
   - Check Alembic migration history under `/backend/alembic/versions`.
   - Check installed dependencies in `pyproject.toml` or `package.json`.
2. **Reusability Identification**:
   - Identify existing domain models, utility functions, or middleware that can be reused.
   - Prevent duplicated schemas or overlapping router endpoints.
3. **Impact & Risk Assessment**:
   - Identify cascading impacts on foreign keys, existing tests, or frontend hooks before proposing changes.
