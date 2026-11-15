---
name: api-testing
description: Execute HTTP request/response testing against FastAPI endpoints using httpx AsyncClient.
---

# API Testing Skill

## Purpose
Validates HTTP contracts, status codes, query parameters, payload serialization, and error envelopes.

## Guidelines
1. **Status Code Accuracy**: Verify standard responses (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found).
2. **Payload Validation**: Test with missing required fields, invalid types, and boundary-exceeding string lengths.
3. **Draft Shielding**: Verify that student tokens cannot retrieve evaluations or reviews in `DRAFT` or `PENDING_REVIEW` states.
