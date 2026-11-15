---
name: frontend-testing
description: Test React components, form validations, interactive canvas tools, and state hooks using Vitest and RTL.
---

# Frontend Testing Skill

## Purpose
Verifies user interface reliability, accessibility, and error handling across React components.

## Guidelines
1. **Interactive Canvas**: Test `MistakeCard` accept/reject triggers and `RubricScoreSliders` score updates.
2. **Editor Constraints**: Verify character/word counters and offline autosave persistence to `localStorage`.
3. **Production Sanitization**: Confirm that `DevRoleSwitcher` is not rendered when `NODE_ENV=production`.
