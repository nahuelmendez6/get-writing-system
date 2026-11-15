---
name: database-development
description: Design SQLAlchemy 2.0 declarative models, write Alembic migrations, and optimize PostgreSQL indexes.
---

# Database Development Skill

## Purpose
Enables the Implementer to build robust relational schemas and maintain safe migration histories.

## Guidelines
1. **Declarative Syntax**: Use modern SQLAlchemy 2.0 `Mapped` type annotations and `mapped_column()`.
2. **Key Conventions**: Use UUIDv4 primary keys and explicit foreign keys with `ondelete` strategies.
3. **Reversible Migrations**: Test both `upgrade()` and `downgrade()` for every new Alembic revision.
4. **Performance**: Add B-tree indexes to foreign keys, lookup fields, and query filter columns.
