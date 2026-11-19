from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RedactionItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(
        ..., description="PII category (EMAIL, PHONE, ID, STUDENT_NAME, etc.)"
    )
    replacement_token: str = Field(..., description="Masked placeholder token")
    value_hash: str = Field(..., description="SHA-256 non-reversible hash for audit")


class SanitizeTextRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ..., min_length=1, max_length=50000, description="Raw student text to sanitize"
    )
    custom_entities: list[str] | None = Field(
        default=None,
        description="Optional list of specific entity names to sanitize (e.g. known student full name)",
    )


class SanitizeTextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    original_length: int = Field(..., ge=0, description="Character count of raw text")
    sanitized_text: str = Field(
        ..., description="Sanitized text with masked PII placeholders"
    )
    pii_detected_count: int = Field(
        ..., ge=0, description="Total count of PII entities found and sanitized"
    )
    pii_types: list[str] = Field(
        default_factory=list, description="Unique categories of PII detected"
    )
    word_count: int = Field(..., ge=0, description="Word count of the sanitized text")
    redactions: list[RedactionItem] = Field(
        default_factory=list, description="Audit log of sanitized items"
    )


class ZDRStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    zdr_enforced: bool = Field(..., description="Whether Zero Data Retention is active")
    active_provider: str = Field(..., description="Active configured LLM provider")
    supported_providers: list[str] = Field(
        ..., description="List of supported LLM providers"
    )
    retention_policy: str = Field(
        ..., description="Active data retention policy identifier"
    )
    gdpr_minor_protection_active: bool = Field(
        ..., description="Whether GDPR minor compliance rules are active"
    )
    headers_injected: list[str] = Field(
        ..., description="List of mandatory ZDR HTTP headers injected"
    )


class GuardianConsentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    guardian_name: str = Field(
        ..., min_length=2, max_length=150, description="Full name of legal guardian"
    )
    guardian_email: str = Field(
        ..., max_length=255, description="Email address of legal guardian"
    )
    guardian_phone: str = Field(
        ..., max_length=50, description="Phone number of legal guardian"
    )
    relationship: Literal["PARENT", "LEGAL_GUARDIAN"] = Field(
        ...,
        description="Relationship to student (PARENT or LEGAL_GUARDIAN)",
    )
    verification_method: Literal[
        "DIGITAL_SIGNATURE", "VERIFIED_EMAIL", "ACADEMY_PAPER"
    ] = Field(
        ...,
        description="Verification method used for parental consent",
    )
    consent_date: date = Field(
        ..., description="Date when guardian consent was granted"
    )
    document_hash: str = Field(
        ..., min_length=16, description="Cryptographic hash of the consent document"
    )
    status: Literal["ACTIVE", "REVOKED", "EXPIRED"] = Field(
        default="ACTIVE",
        description="Current status of the consent record",
    )


class MinorConsentValidationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    birth_date: date = Field(..., description="Student birth date")
    guardian_consent: GuardianConsentSchema | None = Field(
        default=None,
        description="Legal guardian consent details if student is under 14",
    )
    reference_date: date | None = Field(
        default=None,
        description="Optional reference date for age calculation (defaults to current date)",
    )


class MinorConsentValidationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_minor: bool = Field(..., description="True if age < 18")
    student_age: int = Field(
        ..., ge=0, description="Calculated student age in completed years"
    )
    requires_guardian_consent: bool = Field(
        ..., description="True if age < 14 under Spanish LOPDGDD"
    )
    is_valid: bool = Field(
        ..., description="True if consent criteria are satisfied to proceed"
    )
    legal_basis: str = Field(..., description="GDPR / LOPDGDD legal basis description")
    errors: list[str] = Field(
        default_factory=list, description="Validation failure messages if any"
    )


class ErasureRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: str = Field(..., description="Student identifier")
    submission_text: str = Field(
        ..., description="Student text submission to erase/pseudonymize"
    )
    photo_paths: list[str] | None = Field(
        default=None, description="Optional associated image paths to purge"
    )


class ErasureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certificate_id: str = Field(..., description="Unique certificate UUID")
    student_id_hash: str = Field(
        ..., description="SHA-256 hash of the student identifier"
    )
    erased_at: datetime = Field(
        ..., description="Timestamp of erasure execution in UTC"
    )
    erased_items: list[str] = Field(
        ..., description="List of components and paths erased"
    )
    verification_hash: str = Field(
        ..., description="Cryptographic verification signature hash"
    )
    status: str = Field(
        default="COMPLETED", description="Status of the erasure operation"
    )
