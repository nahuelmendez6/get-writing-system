import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings

DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"
FORMULAIC_GREETINGS = {
    "sir",
    "madam",
    "editor",
    "reader",
    "all",
    "customer",
    "member",
    "team",
    "whom it may concern",
}


@dataclass
class RedactionEntry:
    """Record of an individual PII entity redacted from text."""

    category: str
    replacement_token: str
    value_hash: str
    match_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "replacement_token": self.replacement_token,
            "value_hash": self.value_hash,
        }


@dataclass
class SanitizationResult:
    """Outcome of PII anonymization filtering."""

    clean_text: str
    pii_detected_count: int
    pii_types: list[str] = field(default_factory=list)
    redactions: list[RedactionEntry] = field(default_factory=list)


class PIISanitizer:
    """Comprehensive Personally Identifiable Information (PII) anonymization filter."""

    @staticmethod
    def _hash_val(val: str) -> str:
        """Create a non-reversible SHA-256 hash for audit trails without leaking PII."""
        return hashlib.sha256(val.strip().lower().encode("utf-8")).hexdigest()[:16]

    @classmethod
    def is_valid_dni(cls, dni_str: str) -> bool:
        """Validate Spanish DNI format and control letter checksum (mod 23)."""
        clean = re.sub(r"[- ]", "", dni_str).strip().upper()
        if len(clean) != 9 or not clean[:8].isdigit() or not clean[8].isalpha():
            return False
        num = int(clean[:8])
        expected_letter = DNI_LETTERS[num % 23]
        return clean[8] == expected_letter

    @classmethod
    def is_valid_nie(cls, nie_str: str) -> bool:
        """Validate Spanish NIE format (X, Y, Z prefix) and control letter checksum."""
        clean = re.sub(r"[- ]", "", nie_str).strip().upper()
        if (
            len(clean) != 9
            or clean[0] not in "XYZ"
            or not clean[1:8].isdigit()
            or not clean[8].isalpha()
        ):
            return False
        prefix_val = {"X": "0", "Y": "1", "Z": "2"}[clean[0]]
        num = int(prefix_val + clean[1:8])
        expected_letter = DNI_LETTERS[num % 23]
        return clean[8] == expected_letter

    @classmethod
    def sanitize(
        cls,
        text: str,
        custom_entities: list[str] | None = None,
        force: bool = False,
    ) -> SanitizationResult:
        """Strip all sensitive PII markers and replace with standardized tokens."""
        if not text:
            return SanitizationResult(clean_text="", pii_detected_count=0)

        if not force and not settings.SANITIZE_PII:
            return SanitizationResult(clean_text=text, pii_detected_count=0)

        redactions: list[RedactionEntry] = []
        result = text

        # 1. Custom entities (if provided by caller, e.g. student name from enrollment)
        if custom_entities:
            for entity in custom_entities:
                if entity and len(entity.strip()) >= 3:
                    escaped = re.escape(entity.strip())
                    pattern = rf"\b{escaped}\b"
                    matches = list(re.finditer(pattern, result, flags=re.IGNORECASE))
                    for m in matches:
                        val = m.group(0)
                        redactions.append(
                            RedactionEntry(
                                category="STUDENT_NAME",
                                replacement_token="[STUDENT_NAME_REDACTED]",
                                value_hash=cls._hash_val(val),
                            )
                        )
                    result = re.sub(
                        pattern, "[STUDENT_NAME_REDACTED]", result, flags=re.IGNORECASE
                    )

        # 2. Email addresses
        email_pattern = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"
        for m in re.finditer(email_pattern, result):
            redactions.append(
                RedactionEntry(
                    category="EMAIL",
                    replacement_token="[EMAIL_REDACTED]",
                    value_hash=cls._hash_val(m.group(0)),
                )
            )
        result = re.sub(email_pattern, "[EMAIL_REDACTED]", result)

        # 3. Spanish DNI and NIE numbers
        id_pattern = r"\b(?:\d{8}[- ]?[A-Za-z]|[XYZxyz]\d{7}[- ]?[A-Za-z])\b"
        matches = list(re.finditer(id_pattern, result))
        # Replace in reverse order of appearance to maintain index validity if needed
        for m in matches:
            val = m.group(0)
            if cls.is_valid_dni(val) or cls.is_valid_nie(val):
                redactions.append(
                    RedactionEntry(
                        category="ID",
                        replacement_token="[ID_REDACTED]",
                        value_hash=cls._hash_val(val),
                    )
                )
                result = result.replace(val, "[ID_REDACTED]")

        # 4. Explicit Passport / Generic ID mentions
        passport_pattern = (
            r"\b(?:passport|pasaporte|dni|nie|national id|id number|student id)"
            r"(?:\s*[:#-]?\s*)([A-Za-z0-9]{6,12})\b"
        )
        for m in re.finditer(passport_pattern, result, flags=re.IGNORECASE):
            full_match = m.group(0)
            val = m.group(1)
            redactions.append(
                RedactionEntry(
                    category="ID",
                    replacement_token="[ID_REDACTED]",
                    value_hash=cls._hash_val(val),
                )
            )
            result = result.replace(
                full_match, f"{full_match.split(val)[0]}[ID_REDACTED]"
            )

        # 5. Phone numbers (Spanish formats and international)
        phone_patterns = [
            r"(?:\+?34[\s.-]?)?(?:[6789]\d{2}[\s.-]?\d{3}[\s.-]?\d{3})\b",
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            r"\b\+\d{1,4}[-.\s]?(?:\(?\d{1,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b",
        ]
        for pat in phone_patterns:
            for m in re.finditer(pat, result):
                val = m.group(0).strip()
                # Exclude simple years or short numbers
                if len(re.sub(r"\D", "", val)) >= 9:
                    redactions.append(
                        RedactionEntry(
                            category="PHONE",
                            replacement_token="[PHONE_REDACTED]",
                            value_hash=cls._hash_val(val),
                        )
                    )
                    result = result.replace(val, "[PHONE_REDACTED]")

        # 6. Usernames / Social Handles (@handle)
        handle_pattern = r"(?<!\w)@[a-zA-Z0-9_.-]{3,30}\b"
        for m in re.finditer(handle_pattern, result):
            val = m.group(0)
            redactions.append(
                RedactionEntry(
                    category="STUDENT_NAME",
                    replacement_token="[STUDENT_NAME_REDACTED]",
                    value_hash=cls._hash_val(val),
                )
            )
            result = result.replace(val, "[STUDENT_NAME_REDACTED]")

        # 7. Self-introductions and Student Names ("My name is John Doe", "I am Maria Perez")
        intro_pattern = r"\b(?:my name is|i am|i'm|me llamo|soy)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b"
        for m in re.finditer(intro_pattern, result, flags=re.IGNORECASE):
            name_val = m.group(1).strip()
            redactions.append(
                RedactionEntry(
                    category="STUDENT_NAME",
                    replacement_token="[STUDENT_NAME_REDACTED]",
                    value_hash=cls._hash_val(name_val),
                )
            )
            result = result.replace(name_val, "[STUDENT_NAME_REDACTED]")

        # 8. Signatures & Letter Closings ("Yours sincerely, Carlos Gomez", "Signed: John Smith")
        closing_pattern = (
            r"\b(?:Sincerely|Yours sincerely|Yours faithfully|Best regards|Warm regards|"
            r"Kind regards|Regards|Best wishes|Love|Yours truly|Signed)"
            r"[,:]?\s*(?:\n|\r\n)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
        )
        for m in re.finditer(closing_pattern, result, flags=re.IGNORECASE):
            name_val = m.group(1).strip()
            # Ensure it's not a standard closing continuation or generic role
            if (
                name_val
                and name_val.lower() not in FORMULAIC_GREETINGS
                and len(name_val) >= 3
            ):
                redactions.append(
                    RedactionEntry(
                        category="STUDENT_NAME",
                        replacement_token="[STUDENT_NAME_REDACTED]",
                        value_hash=cls._hash_val(name_val),
                    )
                )
                result = result.replace(name_val, "[STUDENT_NAME_REDACTED]")

        # 9. Letter Greetings with Personal Names ("Dear John Doe," excluding formulaic "Dear Sir or Madam" or titles "Dear Mr. Davis")
        greeting_pattern = (
            r"\b(?:Dear|Hi|Hello|Hey)\s+"
            r"(?!(?:Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.|Sir|Madam|Editor|All)(?:\s|\b))"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
        )
        for m in re.finditer(greeting_pattern, result):
            salutation_target = m.group(1).strip()
            if salutation_target.lower() not in FORMULAIC_GREETINGS:
                redactions.append(
                    RedactionEntry(
                        category="STUDENT_NAME",
                        replacement_token="[NAME_REDACTED]",
                        value_hash=cls._hash_val(salutation_target),
                    )
                )
                result = result.replace(salutation_target, "[NAME_REDACTED]")

        # 10. Educational Institutions & Academies
        institution_pattern = (
            r"\b(?:Get\s+Idiomas|Get\s+Languages|Cambridge\s+(?:Academy|School|Institute)|"
            r"IES\s+[A-Za-z0-9_-]+|Colegio\s+[A-Za-z0-9_-]+|Academia\s+[A-Za-z0-9_-]+)\b"
        )
        for m in re.finditer(institution_pattern, result, flags=re.IGNORECASE):
            val = m.group(0)
            redactions.append(
                RedactionEntry(
                    category="INSTITUTION",
                    replacement_token="[INSTITUTION_REDACTED]",
                    value_hash=cls._hash_val(val),
                )
            )
            result = result.replace(val, "[INSTITUTION_REDACTED]")

        # 11. Instructors & Teachers
        instructor_pattern = r"\b(?:Teacher|Prof\.|Professor|Profesor|Profesora|Mr\.|Mrs\.|Ms\.)\s+[A-Z][a-z]+\b"
        for m in re.finditer(instructor_pattern, result):
            val = m.group(0)
            redactions.append(
                RedactionEntry(
                    category="INSTRUCTOR",
                    replacement_token="[INSTRUCTOR_REDACTED]",
                    value_hash=cls._hash_val(val),
                )
            )
            result = result.replace(val, "[INSTRUCTOR_REDACTED]")

        # 12. Physical Addresses and Spanish Postal Codes
        address_patterns = [
            r"\b(?:Calle|C\/|Avda\.?|Avenida|Paseo|Plaza|Road|Street|St\.?|Avenue|Ave\.?)\s+[A-Z0-9][a-zA-Z0-9\s,.-]+?\d{1,4}\b",
            r"\b(?:0[1-9]|[1-4]\d|5[0-2])\d{3}\b",  # Spanish Postal Code
        ]
        for pat in address_patterns:
            for m in re.finditer(pat, result):
                val = m.group(0)
                redactions.append(
                    RedactionEntry(
                        category="ADDRESS",
                        replacement_token="[ADDRESS_REDACTED]",
                        value_hash=cls._hash_val(val),
                    )
                )
                result = result.replace(val, "[ADDRESS_REDACTED]")

        unique_types = sorted({r.category for r in redactions})

        return SanitizationResult(
            clean_text=result,
            pii_detected_count=len(redactions),
            pii_types=unique_types,
            redactions=redactions,
        )


def sanitize_pii(
    text: str, custom_entities: list[str] | None = None
) -> SanitizationResult:
    """Convenience helper to sanitize text using PIISanitizer."""
    return PIISanitizer.sanitize(text, custom_entities=custom_entities)
