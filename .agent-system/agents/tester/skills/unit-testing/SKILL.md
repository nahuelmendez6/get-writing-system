---
name: unit-testing
description: Author and execute isolated unit tests for services, business rules, formulas, and schema validators.
---

# Unit Testing Skill

## Purpose
Ensures individual software functions, grading calculators, and validators operate with mathematical precision.

## Guidelines
1. **Cambridge Grade Calculations**: Validate the 10-point conversion formula across all edge cases (all 0s, all 5s, half-bands).
2. **Schema & Model Validation**: Verify Pydantic validators reject out-of-range bands, malformed emails, and invalid submission states.
3. **Mocking External Boundaries**: Mock database calls, S3 interactions, and external LLM APIs when executing pure unit tests.
