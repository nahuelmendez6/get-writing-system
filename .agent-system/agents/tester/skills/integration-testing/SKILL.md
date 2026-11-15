---
name: integration-testing
description: Validate database persistence, asynchronous Celery queues, and inter-service communication pipelines.
---

# Integration Testing Skill

## Purpose
Verifies that database engines, caching layers, and decoupled services collaborate correctly without data loss.

## Guidelines
1. **Database Transactions & Rollbacks**: Test that SQLAlchemy sessions roll back cleanly on errors and migrations apply idempotently.
2. **Celery Worker Pipelines**: Test async task dispatch and execution using Celery test configurations (`task_always_eager` or local Redis).
3. **Decoupled Engine Communication**: Test internal backend-to-AI-service HTTP calls with mock LLM responses.
