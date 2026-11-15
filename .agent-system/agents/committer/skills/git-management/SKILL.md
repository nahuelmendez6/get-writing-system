---
name: git-management
description: Manage Git staging, atomic commits, branch hygiene, and clean working tree verification.
---

# Git Management Skill

## Purpose
Ensures disciplined version control operations, preventing corrupted states or accidental leaks of secrets.

## Guidelines
1. **Working Tree Sanitation**: Run `git status --porcelain` to verify only relevant task files are present.
2. **Selective Staging**: Use `git add <file>` explicitly rather than `git add .` to avoid capturing unintended scratch files.
3. **Rollback Safety**: In case of commit hook or signing errors, restore working trees safely without data loss.
