from app.core.sanitizer import PIISanitizer, sanitize_pii


def test_dni_validation() -> None:
    # 12345678Z is a mathematically valid Spanish DNI
    assert PIISanitizer.is_valid_dni("12345678Z") is True
    assert PIISanitizer.is_valid_dni("12345678-Z") is True
    assert PIISanitizer.is_valid_dni("12345678A") is False  # Wrong letter
    assert PIISanitizer.is_valid_dni("12345") is False


def test_nie_validation() -> None:
    # X1234567L is a valid Spanish NIE (01234567 % 23 = 19 -> L)
    assert PIISanitizer.is_valid_nie("X1234567L") is True
    assert PIISanitizer.is_valid_nie("X-1234567-L") is True
    assert PIISanitizer.is_valid_nie("X1234567A") is False  # Wrong letter
    assert PIISanitizer.is_valid_nie("A1234567L") is False  # Invalid prefix


def test_sanitize_emails_and_phones() -> None:
    text = "Please write to student.test@cambridge.org or call +34 612 345 678 immediately."
    res = PIISanitizer.sanitize(text)

    assert "[EMAIL_REDACTED]" in res.clean_text
    assert "student.test@cambridge.org" not in res.clean_text
    assert "[PHONE_REDACTED]" in res.clean_text
    assert "+34 612 345 678" not in res.clean_text
    assert "EMAIL" in res.pii_types
    assert "PHONE" in res.pii_types
    assert res.pii_detected_count >= 2


def test_sanitize_dni_and_nie() -> None:
    text = "My Spanish DNI is 12345678Z and my foreign NIE is X1234567L."
    res = PIISanitizer.sanitize(text)

    assert "[ID_REDACTED]" in res.clean_text
    assert "12345678Z" not in res.clean_text
    assert "X1234567L" not in res.clean_text
    assert "ID" in res.pii_types
    assert res.pii_detected_count >= 2


def test_sanitize_passport() -> None:
    text = "My passport: AB1234567 issued in 2024."
    res = PIISanitizer.sanitize(text)

    assert "[ID_REDACTED]" in res.clean_text
    assert "AB1234567" not in res.clean_text
    assert "ID" in res.pii_types


def test_sanitize_student_names_and_signatures() -> None:
    text = (
        "Dear Carlos,\n"
        "My name is John Doe.\n"
        "I am writing this essay about environment.\n"
        "Yours sincerely,\n"
        "John Doe"
    )
    res = PIISanitizer.sanitize(text)

    assert "John Doe" not in res.clean_text
    assert "[STUDENT_NAME_REDACTED]" in res.clean_text
    assert "[NAME_REDACTED]" in res.clean_text
    assert "STUDENT_NAME" in res.pii_types


def test_preserves_formulaic_greetings() -> None:
    text = "Dear Sir or Madam, I am writing to express my dissatisfaction. Dear Editor, I agree with the article."
    res = PIISanitizer.sanitize(text)

    assert "Dear Sir or Madam" in res.clean_text
    assert "Dear Editor" in res.clean_text


def test_sanitize_institutions_and_instructors() -> None:
    text = "I attend Get Idiomas and my teacher is Teacher Smith, assisted by Prof. Garcia at Cambridge Academy."
    res = PIISanitizer.sanitize(text)

    assert "Get Idiomas" not in res.clean_text
    assert "Teacher Smith" not in res.clean_text
    assert "Cambridge Academy" not in res.clean_text
    assert "[INSTITUTION_REDACTED]" in res.clean_text
    assert "[INSTRUCTOR_REDACTED]" in res.clean_text
    assert "INSTITUTION" in res.pii_types
    assert "INSTRUCTOR" in res.pii_types


def test_sanitize_addresses_and_postal_codes() -> None:
    text = "The academy is located at Calle Mayor 45, 28001 Madrid."
    res = PIISanitizer.sanitize(text)

    assert "Calle Mayor 45" not in res.clean_text
    assert "28001" not in res.clean_text
    assert "[ADDRESS_REDACTED]" in res.clean_text
    assert "ADDRESS" in res.pii_types


def test_sanitize_custom_entities() -> None:
    text = "This essay was submitted by nahuelito for evaluation."
    res = PIISanitizer.sanitize(text, custom_entities=["nahuelito"])

    assert "nahuelito" not in res.clean_text
    assert "[STUDENT_NAME_REDACTED]" in res.clean_text
    assert res.pii_detected_count >= 1


def test_sanitize_handles_empty_text() -> None:
    res = sanitize_pii("")
    assert res.clean_text == ""
    assert res.pii_detected_count == 0
    assert res.pii_types == []
