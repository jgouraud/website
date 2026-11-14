"""Regression checks for user-controlled query normalization and asset paths."""

from pathlib import Path

import pytest

import utils


@pytest.mark.parametrize(
    ('raw', 'expected'),
    [
        ('en', 'EN'),
        ('FR', 'FR'),
        ('fr', 'FR'),
        ('DE', 'EN'),
        ('', 'EN'),
        (None, 'EN'),
    ],
)
def test_language_normalization_accepts_only_supported_languages(raw, expected):
    assert utils.normalized_language(raw) == expected


def test_localized_text_uses_english_fallback():
    assert utils.localized({'en': 'Hello', 'fr': 'Bonjour'}, 'fr') == 'Bonjour'
    assert utils.localized({'en': 'Hello'}, 'fr') == 'Hello'
    assert utils.localized(None, 'en') == ''


def test_asset_url_encodes_spaces_and_updates_when_file_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, 'ASSET_DIR', tmp_path)
    file = tmp_path / 'example illustration.svg'
    assert utils.asset_url(file.name).endswith('?v=0')
    file.write_text('<svg/>', encoding='utf-8')
    assert utils.asset_url(file.name) == (
        '/assets/example%20illustration.svg?v=' + str(file.stat().st_mtime_ns)
    )


@pytest.mark.parametrize('filename', ['', '.', '..', '../secret', '/tmp/secret', 'path\\secret'])
def test_asset_url_refuses_paths_outside_assets(filename):
    with pytest.raises(ValueError):
        utils.asset_url(filename)


def test_business_url_preserves_language():
    assert utils.business_url('FR') == '/?lang=FR#business-solutions'
