"""Language-normalization for text sent to CLIP."""

import logging

from deep_translator import GoogleTranslator
from deep_translator.exceptions import BaseError
from requests.exceptions import RequestException

from search_engine.validation import validate_description


LOGGER = logging.getLogger('partfinder')


def translate_to_english(text: str) -> str:
    """Translate when available; use the original query if the optional provider fails."""
    query = validate_description(text)
    if not query:
        return ''
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(query)
    except (BaseError, RequestException) as exc:
        LOGGER.warning('translation_unavailable error_type=%s', type(exc).__name__)
        return query
    if not isinstance(translated, str):
        LOGGER.warning('translation_invalid_response')
        return query
    return validate_description(translated)
