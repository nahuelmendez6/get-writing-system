---
name: security-testing
description: Audit RBAC role boundaries, object ownership, Zero Data Retention compliance, and PII anonymization.
---

# Security Testing Skill

## Purpose
Validates system security postures, ensuring compliance with GDPR, ZDR, and access control mandates.

## Guidelines
1. **RBAC & Ownership Matrix**:
   - Verify students cannot access other students' submissions or teacher reviews.
   - Verify teachers cannot modify assignments of courses they do not teach.
   - Verify non-admin users cannot alter user roles or inspect audit logs.
2. **PII Anonymization Filter**:
   - Pass synthetic texts containing names, emails, and phone numbers through `sanitizer.py` and verify all PII is replaced with tokens.
3. **ZDR Verification**:
   - Verify all outward LLM requests include mandatory Zero Data Retention headers and flags.
4. **Credential Restrictions**:
   - Verify that attempts to use DNI as a login password or bypass password policies are rejected.
