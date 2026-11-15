---
name: api-integration
description: Wire up background Celery workers, internal AI service calls, and S3 presigned URL storage flows.
---

# API Integration Skill

## Purpose
Enables the Implementer to integrate asynchronous queues, internal service gateways, and object storage.

## Guidelines
1. **Asynchronous Dispatch**: Offload long-running AI evaluations to Celery tasks using Redis as the message broker.
2. **Internal API Client**: Communicate with `ai_service` via authenticated HTTP client (`httpx.AsyncClient`) with connection pooling and timeouts.
3. **Presigned S3 URLs**: Implement pre-signed `PUT` and `GET` URL generators with a maximum 15-minute TTL.
