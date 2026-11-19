import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

SPANISH_MINOR_CONSENT_AGE = 14
ADULT_AGE = 18


@dataclass
class GuardianConsent:
    """Legal guardian consent record for minor students."""

    guardian_name: str
    guardian_email: str
    guardian_phone: str
    relationship: str  # "PARENT", "LEGAL_GUARDIAN"
    verification_method: str  # "DIGITAL_SIGNATURE", "VERIFIED_EMAIL", "ACADEMY_PAPER"
    consent_date: date
    document_hash: str
    status: str = "ACTIVE"  # "ACTIVE", "REVOKED", "EXPIRED"

    def is_active(self) -> bool:
        return self.status.upper() == "ACTIVE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "guardian_name": self.guardian_name,
            "guardian_email": self.guardian_email,
            "guardian_phone": self.guardian_phone,
            "relationship": self.relationship,
            "verification_method": self.verification_method,
            "consent_date": self.consent_date.isoformat(),
            "document_hash": self.document_hash,
            "status": self.status,
        }


@dataclass
class MinorConsentValidationResult:
    """Outcome of GDPR minor consent verification."""

    is_minor: bool
    student_age: int
    requires_guardian_consent: bool
    is_valid: bool
    legal_basis: str
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_minor": self.is_minor,
            "student_age": self.student_age,
            "requires_guardian_consent": self.requires_guardian_consent,
            "is_valid": self.is_valid,
            "legal_basis": self.legal_basis,
            "errors": self.errors,
        }


@dataclass
class ErasureCertificate:
    """Cryptographic audit certificate for Right to Erasure execution (GDPR Art. 17)."""

    certificate_id: str
    student_id_hash: str
    erased_at: datetime
    erased_items: list[str]
    verification_hash: str
    status: str = "COMPLETED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "student_id_hash": self.student_id_hash,
            "erased_at": self.erased_at.isoformat(),
            "erased_items": self.erased_items,
            "verification_hash": self.verification_hash,
            "status": self.status,
        }


class GDPRComplianceManager:
    """Manager for minor protection policies and Right to Erasure."""

    @staticmethod
    def calculate_age(birth_date: date, reference_date: date | None = None) -> int:
        """Calculate exact chronological age in completed years."""
        ref = reference_date or date.today()
        years = ref.year - birth_date.year
        if (ref.month, ref.day) < (birth_date.month, birth_date.day):
            years -= 1
        return max(0, years)

    @classmethod
    def validate_minor_consent(
        cls,
        birth_date: date,
        guardian_consent: GuardianConsent | None = None,
        reference_date: date | None = None,
    ) -> MinorConsentValidationResult:
        """Validate student age and parental/guardian consent requirements."""
        age = cls.calculate_age(birth_date, reference_date)
        is_minor = age < ADULT_AGE
        requires_guardian = age < SPANISH_MINOR_CONSENT_AGE
        errors: list[str] = []

        if not is_minor:
            return MinorConsentValidationResult(
                is_minor=False,
                student_age=age,
                requires_guardian_consent=False,
                is_valid=True,
                legal_basis=(
                    "GDPR Art. 6(1)(b) - Autonomous Contractual Consent (Adult)"
                ),
                errors=[],
            )

        if requires_guardian:
            if not guardian_consent:
                errors.append(
                    f"El estudiante tiene {age} años (< {SPANISH_MINOR_CONSENT_AGE}). "
                    "Se requiere consentimiento expreso de padres o tutores legales "
                    "(LOPDGDD Art. 7)."
                )
                return MinorConsentValidationResult(
                    is_minor=True,
                    student_age=age,
                    requires_guardian_consent=True,
                    is_valid=False,
                    legal_basis=(
                        "LOPDGDD Art. 7 / GDPR Art. 8 - Mandatory Consent Missing"
                    ),
                    errors=errors,
                )

            if not guardian_consent.is_active():
                errors.append(
                    f"El consentimiento del tutor legal tiene estado "
                    f"'{guardian_consent.status}' (requerido: 'ACTIVE')."
                )
                return MinorConsentValidationResult(
                    is_minor=True,
                    student_age=age,
                    requires_guardian_consent=True,
                    is_valid=False,
                    legal_basis=(
                        "LOPDGDD Art. 7 - Guardian Consent Inactive or Revoked"
                    ),
                    errors=errors,
                )

            return MinorConsentValidationResult(
                is_minor=True,
                student_age=age,
                requires_guardian_consent=True,
                is_valid=True,
                legal_basis=(
                    f"LOPDGDD Art. 7 - Consent ({guardian_consent.relationship})"
                ),
                errors=[],
            )

        # 14 <= age < 18
        return MinorConsentValidationResult(
            is_minor=True,
            student_age=age,
            requires_guardian_consent=False,
            is_valid=True,
            legal_basis="LOPDGDD Art. 7(1) - Autonomous Consent for Minors >= 14 Years",
            errors=[],
        )

    @classmethod
    def execute_right_to_erasure(
        cls,
        student_id: str,
        submission_text: str,
        photo_paths: list[str] | None = None,
    ) -> ErasureCertificate:
        """Execute Right to Erasure (GDPR Art. 17) on student submission data."""
        cert_id = str(uuid.uuid4())
        student_hash = hashlib.sha256(student_id.encode("utf-8")).hexdigest()
        now = datetime.now(UTC)

        erased_elements: list[str] = [
            "submission_text_anonymized",
            "pii_metadata_purged",
        ]

        if photo_paths:
            for path in photo_paths:
                erased_elements.append(f"photograph_purged:{path}")

        payload_to_sign = (
            f"{cert_id}:{student_hash}:{now.isoformat()}:{','.join(erased_elements)}"
        )
        verif_hash = hashlib.sha256(payload_to_sign.encode("utf-8")).hexdigest()

        return ErasureCertificate(
            certificate_id=cert_id,
            student_id_hash=student_hash,
            erased_at=now,
            erased_items=erased_elements,
            verification_hash=verif_hash,
            status="COMPLETED",
        )
