from datetime import date

from app.core.gdpr import GDPRComplianceManager, GuardianConsent


def test_calculate_age_exact() -> None:
    ref = date(2026, 11, 19)
    # Exactly 13 years old
    assert GDPRComplianceManager.calculate_age(date(2013, 11, 19), ref) == 13
    # Birthday not reached yet in current year (turns 14 tomorrow)
    assert GDPRComplianceManager.calculate_age(date(2012, 11, 20), ref) == 13
    # Turned 14 yesterday
    assert GDPRComplianceManager.calculate_age(date(2012, 11, 18), ref) == 14


def test_validate_minor_under_14_without_guardian_fails() -> None:
    ref = date(2026, 11, 19)
    # 12 years old
    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2014, 5, 10),
        guardian_consent=None,
        reference_date=ref,
    )

    assert res.is_minor is True
    assert res.student_age == 12
    assert res.requires_guardian_consent is True
    assert res.is_valid is False
    assert len(res.errors) >= 1
    assert "LOPDGDD Art. 7" in res.errors[0]


def test_validate_minor_under_14_with_active_guardian_succeeds() -> None:
    ref = date(2026, 11, 19)
    consent = GuardianConsent(
        guardian_name="Maria Gomez",
        guardian_email="maria.gomez@example.com",
        guardian_phone="+34 600 111 222",
        relationship="PARENT",
        verification_method="DIGITAL_SIGNATURE",
        consent_date=date(2026, 9, 1),
        document_hash="a1b2c3d4e5f6g7h8",
        status="ACTIVE",
    )

    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2014, 5, 10),
        guardian_consent=consent,
        reference_date=ref,
    )

    assert res.is_minor is True
    assert res.student_age == 12
    assert res.requires_guardian_consent is True
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_validate_minor_under_14_with_revoked_guardian_fails() -> None:
    ref = date(2026, 11, 19)
    consent = GuardianConsent(
        guardian_name="Maria Gomez",
        guardian_email="maria.gomez@example.com",
        guardian_phone="+34 600 111 222",
        relationship="PARENT",
        verification_method="VERIFIED_EMAIL",
        consent_date=date(2026, 9, 1),
        document_hash="a1b2c3d4e5f6g7h8",
        status="REVOKED",
    )

    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2014, 5, 10),
        guardian_consent=consent,
        reference_date=ref,
    )

    assert res.is_valid is False
    assert "REVOKED" in res.errors[0]


def test_validate_minor_between_14_and_17_autonomous_consent() -> None:
    ref = date(2026, 11, 19)
    # 15 years old (can consent autonomously in Spain)
    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2011, 4, 15),
        guardian_consent=None,
        reference_date=ref,
    )

    assert res.is_minor is True
    assert res.student_age == 15
    assert res.requires_guardian_consent is False
    assert res.is_valid is True


def test_validate_adult_student() -> None:
    ref = date(2026, 11, 19)
    # 22 years old
    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=date(2004, 1, 1),
        guardian_consent=None,
        reference_date=ref,
    )

    assert res.is_minor is False
    assert res.student_age == 22
    assert res.requires_guardian_consent is False
    assert res.is_valid is True


def test_execute_right_to_erasure() -> None:
    cert = GDPRComplianceManager.execute_right_to_erasure(
        student_id="student-uuid-12345",
        submission_text="My personal writing submission text.",
        photo_paths=["s3://bucket/photo1.jpg", "s3://bucket/photo2.jpg"],
    )

    assert cert.certificate_id is not None
    assert len(cert.student_id_hash) == 64  # SHA-256
    assert cert.status == "COMPLETED"
    assert "submission_text_anonymized" in cert.erased_items
    assert "photograph_purged:s3://bucket/photo1.jpg" in cert.erased_items
    assert len(cert.verification_hash) == 64
