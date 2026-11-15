---
name: backend-development
description: Build scalable, asynchronous FastAPI routers, services, dependencies, and middleware.
---

# Backend Development Skill

## Purpose
Enables the Implementer to build clean, maintainable backend features conforming to the layered architecture.

## Guidelines
1. **Layered Structure**: Keep routers thin; place domain logic in `service.py` and query logic in `repository.py`.
2. **Async DB Operations**: Use `await db.execute()` and `await db.commit()` with SQLAlchemy 2.0 AsyncSession.
3. **Dependency Injection**: Use FastAPI `Depends()` for authentication, DB sessions, and rate limiting.
4. **Exception Handling**: Map domain exceptions to standard `HTTPException` responses with structured error codes.
