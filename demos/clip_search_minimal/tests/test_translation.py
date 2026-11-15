from requests.exceptions import RequestException

from search_engine import translation


def test_translate_to_english_uses_auto_detection(monkeypatch):
    calls = []

    class Translator:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def translate(self, text):
            calls.append(text)
            return 'hex nut'

    monkeypatch.setattr(translation, 'GoogleTranslator', Translator)

    assert translation.translate_to_english('écrou hexagonal') == 'hex nut'
    assert calls == [{'source': 'auto', 'target': 'en'}, 'écrou hexagonal']


def test_empty_query_does_not_call_translation_service(monkeypatch):
    monkeypatch.setattr(translation, 'GoogleTranslator', lambda **_: (_ for _ in ()).throw(AssertionError))

    assert translation.translate_to_english('  ') == ''


def test_provider_failure_falls_back_to_original_query(monkeypatch):
    class OfflineTranslator:
        def __init__(self, **kwargs):
            pass

        def translate(self, text):
            raise RequestException('provider unavailable')

    monkeypatch.setattr(translation, 'GoogleTranslator', OfflineTranslator)
    assert translation.translate_to_english('écrou hexagonal') == 'écrou hexagonal'


def test_invalid_provider_response_falls_back_to_original_query(monkeypatch):
    class InvalidTranslator:
        def __init__(self, **kwargs):
            pass

        def translate(self, text):
            return None

    monkeypatch.setattr(translation, 'GoogleTranslator', InvalidTranslator)
    assert translation.translate_to_english('a toothed gear') == 'a toothed gear'
