from datetime import date

from app.core.gdpr import GDPRComplianceManager, GuardianConsent
from app.schemas.privacy import GuardianConsentSchema, MinorConsentValidationRequest


def test_backend_calculate_age() -> None:
    ref = date(2026, 11, 19)
    assert GDPRComplianceManager.calculate_age(date(2012, 11, 19), ref) == 14
    assert GDPRComplianceManager.calculate_age(date(2012, 11, 20), ref) == 13


def test_backend_minor_consent_validation() -> None:
    ref = date(2026, 11, 19)
    # Under 14 without guardian
    res_under14 = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2015, 3, 1),
        guardian_consent=None,
        reference_date=ref,
    )
    assert res_under14.requires_guardian_consent is True
    assert res_under14.is_valid is False

    # Under 14 with active guardian
    consent = GuardianConsent(
        guardian_name="David Martinez",
        guardian_email="david@example.com",
        guardian_phone="+34 677 888 999",
        relationship="LEGAL_GUARDIAN",
        verification_method="DIGITAL_SIGNATURE",
        consent_date=date(2026, 1, 15),
        document_hash="1122334455667788",
        status="ACTIVE",
    )
    res_valid = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2015, 3, 1),
        guardian_consent=consent,
        reference_date=ref,
    )
    assert res_valid.is_valid is True


def test_backend_privacy_schemas() -> None:
    schema = GuardianConsentSchema(
        guardian_name="Ana Garcia",
        guardian_email="ana@example.com",
        guardian_phone="+34 600 000 111",
        relationship="PARENT",
        verification_method="ACADEMY_PAPER",
        consent_date=date(2026, 10, 1),
        document_hash="hash-1234567890abcdef",
        status="ACTIVE",
    )
    assert schema.relationship == "PARENT"
    assert schema.status == "ACTIVE"

    req = MinorConsentValidationRequest(
        birth_date=date(2014, 5, 20),
        guardian_consent=schema,
    )
    assert req.birth_date == date(2014, 5, 20)
    assert req.guardian_consent is not None
