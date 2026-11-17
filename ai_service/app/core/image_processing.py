"""Image processing and privacy sanitization module for multimodal OCR."""

import base64
import io
import os
from typing import Any

from PIL import Image

# Maximum allowed image size in bytes (15 MB)
MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024

SUPPORTED_FORMATS: dict[str, str] = {
    "JPEG": "image/jpeg",
    "JPG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


class ImageProcessingError(Exception):
    """Raised when an image fails validation or processing."""

    pass


def strip_exif(image_bytes: bytes) -> tuple[bytes, dict[str, Any]]:
    """Sanitizes an image by stripping all EXIF and hardware/geolocation metadata.

    Preserves pixel content and orientation, returning sanitized image bytes
    and safe visual metadata.
    """
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise ImageProcessingError(
            f"Image exceeds maximum allowed size of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB"
        )

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            detected_format = (img.format or "JPEG").upper()
            if detected_format not in SUPPORTED_FORMATS:
                raise ImageProcessingError(
                    f"Unsupported image format '{detected_format}'. Supported formats: {list(SUPPORTED_FORMATS.keys())}"
                )

            # Metadata to keep
            width, height = img.size
            mode = img.mode

            # Convert RGBA to RGB if saving as JPEG
            target_format = "PNG" if detected_format == "PNG" else "JPEG"
            working_img: Image.Image = img
            if target_format == "JPEG" and mode in ("RGBA", "P"):
                working_img = img.convert("RGB")
            elif target_format == "PNG" and mode not in ("RGB", "RGBA", "L"):
                working_img = img.convert("RGBA")

            # Create a clean image object without metadata/EXIF dictionaries
            clean_image = working_img.copy()
            clean_image.info.clear()

            output_buffer = io.BytesIO()
            clean_image.save(output_buffer, format=target_format, quality=95)
            sanitized_bytes = output_buffer.getvalue()

            metadata: dict[str, Any] = {
                "width": width,
                "height": height,
                "original_format": detected_format,
                "sanitized_format": target_format,
                "mime_type": SUPPORTED_FORMATS[target_format],
                "original_size_bytes": len(image_bytes),
                "sanitized_size_bytes": len(sanitized_bytes),
                "exif_stripped": True,
            }

            return sanitized_bytes, metadata

    except ImageProcessingError:
        raise
    except Exception as exc:
        raise ImageProcessingError(f"Failed to process image: {exc}") from exc


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encodes raw image bytes to a base64 UTF-8 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def decode_base64_to_bytes(base64_str: str) -> bytes:
    """Decodes a base64 string to raw image bytes, handling data URI prefixes."""
    clean_str = base64_str.strip()
    if "," in clean_str and clean_str.startswith("data:"):
        clean_str = clean_str.split(",", 1)[1]
    try:
        return base64.b64decode(clean_str)
    except Exception as exc:
        raise ImageProcessingError(f"Invalid base64 image data: {exc}") from exc


def load_and_sanitize_image(source: str | bytes) -> tuple[bytes, str, dict[str, Any]]:
    """Loads an image from file path, raw bytes, or base64 string and strips EXIF.

    Returns:
        (sanitized_bytes, base64_string, metadata_dict)
    """
    if isinstance(source, bytes):
        raw_bytes = source
    elif isinstance(source, str):
        if os.path.isfile(source):
            with open(source, "rb") as f:
                raw_bytes = f.read()
        else:
            raw_bytes = decode_base64_to_bytes(source)
    else:
        raise ImageProcessingError(f"Invalid image source type: {type(source)}")

    sanitized_bytes, metadata = strip_exif(raw_bytes)
    b64_str = encode_image_to_base64(sanitized_bytes)
    return sanitized_bytes, b64_str, metadata
