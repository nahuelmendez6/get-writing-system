---
name: ai-service-development
description: Develop isolated LangGraph pipelines, state nodes, multimodal prompts, and Pydantic output validators.
---

# AI Service Development Skill

## Purpose
Enables the Implementer to develop the automated writing evaluation and multimodal OCR engine using LangGraph.

## Guidelines
1. **LangGraph Pipeline**: Construct state nodes matching the 11-node architecture in `knowledge/ARCHITECTURE.md`.
2. **Pydantic Validation**: Parse all LLM outputs using structured Pydantic models. Catch schema errors and trigger node retries.
3. **Literal OCR Enforcement**: Ensure the transcription prompt preserves exact spelling and punctuation without auto-correcting.
4. **ZDR & Privacy**: Verify that LLM API requests pass explicit Zero Data Retention flags and sanitized student text.
