"""Language-normalization for text sent to CLIP."""

from deep_translator import GoogleTranslator

from search_engine.validation import validate_description


def translate_to_english(text: str) -> str:
    """Detect the source language and return an English query.

    Google Translate's ``auto`` source mode detects the language. English text is
    returned unchanged, while text in another supported language is translated.
    """
    query = validate_description(text)
    if not query:
        return ''
    translated = GoogleTranslator(source='auto', target='en').translate(query)
    if not isinstance(translated, str):
        raise ValueError('The translation service returned an invalid response.')
    return validate_description(translated)
