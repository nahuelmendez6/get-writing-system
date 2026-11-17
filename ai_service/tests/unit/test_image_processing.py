"""Unit tests for image processing and EXIF metadata sanitization."""

import io

import pytest
from PIL import Image

from app.core.image_processing import (
    ImageProcessingError,
    decode_base64_to_bytes,
    encode_image_to_base64,
    load_and_sanitize_image,
    strip_exif,
)


def create_dummy_image(
    format: str = "JPEG", size: tuple[int, int] = (100, 100)
) -> bytes:
    img = Image.new("RGB", size, color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_strip_exif_valid_jpeg() -> None:
    raw_bytes = create_dummy_image("JPEG")
    sanitized_bytes, metadata = strip_exif(raw_bytes)

    assert len(sanitized_bytes) > 0
    assert metadata["sanitized_format"] == "JPEG"
    assert metadata["mime_type"] == "image/jpeg"
    assert metadata["width"] == 100
    assert metadata["height"] == 100
    assert metadata["exif_stripped"] is True


def test_strip_exif_valid_png() -> None:
    raw_bytes = create_dummy_image("PNG", size=(200, 150))
    sanitized_bytes, metadata = strip_exif(raw_bytes)

    assert len(sanitized_bytes) > 0
    assert metadata["sanitized_format"] == "PNG"
    assert metadata["mime_type"] == "image/png"
    assert metadata["width"] == 200
    assert metadata["height"] == 150
    assert metadata["exif_stripped"] is True


def test_strip_exif_invalid_image_raises_error() -> None:
    with pytest.raises(ImageProcessingError):
        strip_exif(b"not-an-image-payload")


def test_base64_roundtrip() -> None:
    raw = create_dummy_image("JPEG")
    b64 = encode_image_to_base64(raw)
    decoded = decode_base64_to_bytes(b64)
    assert len(decoded) == len(raw)


def test_decode_base64_with_data_uri_prefix() -> None:
    raw = create_dummy_image("PNG")
    b64 = encode_image_to_base64(raw)
    data_uri = f"data:image/png;base64,{b64}"
    decoded = decode_base64_to_bytes(data_uri)
    assert len(decoded) == len(raw)


def test_load_and_sanitize_image_from_bytes() -> None:
    raw = create_dummy_image("JPEG", size=(50, 50))
    sanitized_bytes, b64_str, meta = load_and_sanitize_image(raw)
    assert len(sanitized_bytes) > 0
    assert len(b64_str) > 0
    assert meta["width"] == 50
    assert meta["height"] == 50
