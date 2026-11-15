"""Language-normalization for text sent to CLIP."""

import logging

from deep_translator import GoogleTranslator

from search_engine.validation import validate_description


LOGGER = logging.getLogger('partfinder')


def translate_to_english(text: str) -> str:
    """Translate when available; use the original query if the optional provider fails."""
    query = validate_description(text)
    if not query:
        return ''
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(query)
    # Translation is an optional convenience before local CLIP inference. The
    # provider can also fail while parsing a response, which is not always
    # exposed as one of its documented exception types. Never let that make a
    # valid search query unusable.
    except Exception as exc:
        LOGGER.warning('translation_unavailable error_type=%s', type(exc).__name__)
        return query
    if not isinstance(translated, str):
        LOGGER.warning('translation_invalid_response')
        return query
    return validate_description(translated)
