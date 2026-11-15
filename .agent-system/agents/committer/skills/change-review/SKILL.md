---
name: change-review
description: Inspect diffs for stray debug code, credentials, temporary comments, and formatting irregularities.
---

# Change Review Skill

## Purpose
Acts as the final pre-commit inspection line to ensure code cleanliness and secret protection.

## Guidelines
1. **Diff Inspection**: Run `git diff --cached` and scan line-by-line for:
   - Hardcoded API keys, JWT secrets, or database passwords.
   - Stray `print()`, `console.log()`, or breakpoint statements (`pdb`, `debugger`).
   - Commented-out dead blocks of code.
2. **Rejection Trigger**: If any secret or debug remnant is found, unstage the file and notify the Implementer to sanitize before proceeding.
