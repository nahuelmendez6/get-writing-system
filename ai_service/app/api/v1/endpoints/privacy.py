from fastapi import APIRouter, status

from app.core.gdpr import GDPRComplianceManager, GuardianConsent
from app.core.sanitizer import PIISanitizer
from app.core.zdr import ZDRClientManager
from app.schemas.privacy import (
    ErasureRequest,
    ErasureResponse,
    MinorConsentValidationRequest,
    MinorConsentValidationResponse,
    RedactionItem,
    SanitizeTextRequest,
    SanitizeTextResponse,
    ZDRStatusResponse,
)

router = APIRouter(prefix="/privacy", tags=["Privacy & Compliance"])


@router.post(
    "/sanitize",
    response_model=SanitizeTextResponse,
    status_code=status.HTTP_200_OK,
    summary="Sanitize Personally Identifiable Information (PII) from text",
)
async def sanitize_text(payload: SanitizeTextRequest) -> SanitizeTextResponse:
    """Mask student names, emails, phone numbers, DNI/NIE IDs, addresses, and institutions."""
    res = PIISanitizer.sanitize(payload.text, custom_entities=payload.custom_entities)
    words = len(res.clean_text.split()) if res.clean_text else 0
    redaction_items = [
        RedactionItem(
            category=r.category,
            replacement_token=r.replacement_token,
            value_hash=r.value_hash,
        )
        for r in res.redactions
    ]

    return SanitizeTextResponse(
        original_length=len(payload.text),
        sanitized_text=res.clean_text,
        pii_detected_count=res.pii_detected_count,
        pii_types=res.pii_types,
        word_count=words,
        redactions=redaction_items,
    )


@router.get(
    "/status",
    response_model=ZDRStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Zero Data Retention (ZDR) and GDPR compliance status",
)
async def get_privacy_status() -> ZDRStatusResponse:
    """Return system Zero Data Retention compliance settings and active policies."""
    status_data = ZDRClientManager.get_status()
    return ZDRStatusResponse(
        zdr_enforced=status_data["zdr_enforced"],
        active_provider=status_data["active_provider"],
        supported_providers=status_data["supported_providers"],
        retention_policy=status_data["retention_policy"],
        gdpr_minor_protection_active=status_data["gdpr_minor_protection_active"],
        headers_injected=status_data["headers_injected"],
    )


@router.post(
    "/validate-minor-consent",
    response_model=MinorConsentValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate minor age and parental/guardian consent according to GDPR and LOPDGDD",
)
async def validate_minor_consent(
    payload: MinorConsentValidationRequest,
) -> MinorConsentValidationResponse:
    """Verify age threshold (< 14 in Spain) and legal guardian consent status."""
    guardian_consent: GuardianConsent | None = None
    if payload.guardian_consent:
        guardian_consent = GuardianConsent(
            guardian_name=payload.guardian_consent.guardian_name,
            guardian_email=payload.guardian_consent.guardian_email,
            guardian_phone=payload.guardian_consent.guardian_phone,
            relationship=payload.guardian_consent.relationship,
            verification_method=payload.guardian_consent.verification_method,
            consent_date=payload.guardian_consent.consent_date,
            document_hash=payload.guardian_consent.document_hash,
            status=payload.guardian_consent.status,
        )

    res = GDPRComplianceManager.validate_minor_consent(
        birth_date=payload.birth_date,
        guardian_consent=guardian_consent,
        reference_date=payload.reference_date,
    )

    return MinorConsentValidationResponse(
        is_minor=res.is_minor,
        student_age=res.student_age,
        requires_guardian_consent=res.requires_guardian_consent,
        is_valid=res.is_valid,
        legal_basis=res.legal_basis,
        errors=res.errors,
    )


@router.post(
    "/right-to-erasure",
    response_model=ErasureResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Right to Erasure / Right to be Forgotten (GDPR Art. 17)",
)
async def execute_right_to_erasure(payload: ErasureRequest) -> ErasureResponse:
    """Pseudonymize submission text, purge photographic metadata, and issue an audit certificate."""
    cert = GDPRComplianceManager.execute_right_to_erasure(
        student_id=payload.student_id,
        submission_text=payload.submission_text,
        photo_paths=payload.photo_paths,
    )

    return ErasureResponse(
        certificate_id=cert.certificate_id,
        student_id_hash=cert.student_id_hash,
        erased_at=cert.erased_at,
        erased_items=cert.erased_items,
        verification_hash=cert.verification_hash,
        status=cert.status,
    )
