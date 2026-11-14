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
