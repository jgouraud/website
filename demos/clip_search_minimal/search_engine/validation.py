"""Server-side limits shared by the HTTP boundary, UI, and query encoder."""
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_IMAGE_PIXELS = 40_000_000
MAX_PREVIEW_SIDE = 2048
MAX_TEXT_CHARACTERS = 2000
MAX_TEXT_BYTES = 8000
IMAGE_FORMATS = ('PNG', 'JPEG', 'WEBP')


class InputError(ValueError):
    """An expected rejection whose controlled message may be shown to a visitor."""


def validate_description(text: str) -> str:
    if not isinstance(text, str):
        raise InputError('The description must be text.')
    if len(text) > MAX_TEXT_CHARACTERS:
        raise InputError(f'Use at most {MAX_TEXT_CHARACTERS} characters in the description.')
    try:
        encoded = text.encode('utf-8')
    except UnicodeEncodeError as exc:
        raise InputError('The description contains invalid Unicode.') from exc
    if len(encoded) > MAX_TEXT_BYTES:
        raise InputError('The description is too large.')
    if any(ord(character) < 32 and character not in '\n\r\t' for character in text):
        raise InputError('The description contains unsupported control characters.')
    return text.strip()


def validate_image_bytes(data: bytes) -> None:
    if not isinstance(data, bytes) or not data:
        raise InputError('Choose a PNG, JPG, or WEBP image.')
    if len(data) > MAX_IMAGE_BYTES:
        raise InputError('Choose an image smaller than 12 MB.')


def read_reference_image(data: bytes) -> Image.Image:
    """Decode only advertised formats; bound expansion before pixel decoding."""
    validate_image_bytes(data)
    try:
        with Image.open(BytesIO(data), formats=IMAGE_FORMATS) as source:
            if source.width * source.height > MAX_IMAGE_PIXELS:
                raise InputError('Choose an image under 40 megapixels.')
            if getattr(source, 'n_frames', 1) != 1:
                raise InputError('Choose a still image rather than an animation.')
            image = ImageOps.exif_transpose(source).convert('RGB')
            image.thumbnail((MAX_PREVIEW_SIDE, MAX_PREVIEW_SIDE), Image.Resampling.LANCZOS)
            return image.copy()
    except InputError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise InputError('Could not read this image. Choose a valid PNG, JPG, or WEBP.') from exc
