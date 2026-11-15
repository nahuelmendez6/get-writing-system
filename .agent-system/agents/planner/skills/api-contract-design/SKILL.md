---
name: api-contract-design
description: Design typed Pydantic v2 schemas and RESTful API endpoint contracts conforming to FastAPI best practices.
---

# API Contract Design Skill

## Purpose
Enables the Planner agent to specify robust, type-safe API contracts for inter-service and client-server communication.

## Guidelines
1. **Pydantic v2 Best Practices**:
   - Use `BaseModel` with strict field types.
   - Enforce validation rules: `Field(..., min_length=1, max_length=100)`.
   - Always define `ConfigDict(from_attributes=True)` for ORM compatibility.
2. **RESTful Naming Conventions**:
   - Use plural nouns for resource collections (`/api/v1/submissions`, `/api/v1/courses`).
   - Use standard HTTP verbs (`GET`, `POST`, `PATCH`, `DELETE`).
   - Use `/internal/v1/*` for private backend-to-AI-service communication.
3. **Response Envelope Consistency**:
   - Success responses map directly to typed schemas.
   - Error responses adhere to the standard `{ "detail": { "error_code": str, "message": str } }`.
