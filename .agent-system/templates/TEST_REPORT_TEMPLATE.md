# Test Report: [TASK-ID] — [Task Title]

## 1. Metadata
- **Task ID**: `TASK-X.Y`
- **Tester**: Tester Agent
- **Date**: `YYYY-MM-DD`
- **Iteration / Attempt**: `[1 / 2 / 3]`
- **Verdict**: `[APPROVED / REJECTED]`

## 2. Test Execution Summary

| Suite / Category | Total Tests | Passed | Failed | Skipped | Duration |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Unit Tests** | `0` | `0` | `0` | `0` | `0.0s` |
| **Integration Tests** | `0` | `0` | `0` | `0` | `0.0s` |
| **API Endpoints** | `0` | `0` | `0` | `0` | `0.0s` |
| **Security & RBAC** | `0` | `0` | `0` | `0` | `0.0s` |
| **Regression Checks** | `0` | `0` | `0` | `0` | `0.0s` |
| **Total** | `0` | `0` | `0` | `0` | `0.0s` |

- **Code Coverage**: `XX%` (Target: $\ge 80\%$)
- **Static Analysis**: `0 errors / 0 warnings` (`mypy`, `ruff`, `tsc`)

## 3. Acceptance Criteria Validation
- [x] **Scenario 1**: Passed - [Details]
- [x] **Scenario 2**: Passed - [Details]
- [ ] **Scenario 3**: [Failed / Not verified]

## 4. Security & Compliance Verification
- [x] RBAC enforcement verified (Admin, Teacher, Student).
- [x] Ownership checks verified (prevent unauthorized access across courses/submissions).
- [x] No sensitive PII exposed in responses or logs.
- [x] ZDR headers confirmed for AI service calls.

## 5. Identified Defects & Failures (If REJECTED)
*(Leave empty if APPROVED)*

### Defect 1: [Short Title]
- **Failing Test**: `tests/unit/test_auth.py::test_expired_token`
- **Observed Behavior**: Returned HTTP 500 instead of HTTP 401 Unauthorized.
- **Root Cause**: Unhandled `jwt.ExpiredSignatureError` in auth middleware.
- **Required Remediation**: Add exception handler in `modules/auth/dependencies.py`.

## 6. Tester Recommendation
- **Final Decision**: `[APPROVED for Documentation / REJECTED - Hand off to Implementer for Revision]`
