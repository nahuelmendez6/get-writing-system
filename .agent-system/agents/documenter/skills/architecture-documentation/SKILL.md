---
name: architecture-documentation
description: Maintain system topology diagrams and draft Architecture Decision Records (ADRs).
---

# Architecture Documentation Skill

## Purpose
Preserves the long-term architectural integrity of the system by documenting structural patterns and technical decisions.

## Guidelines
1. **ADR Structure**: Follow `templates/ADR_TEMPLATE.md` with explicit context, decision drivers, considered options, and trade-offs.
2. **Mermaid Diagrams**: Use flowcharts and sequence diagrams to illustrate inter-service communications and state transitions.
3. **Decoupling Documentation**: Highlight service boundaries between `backend` and `ai_service`.
