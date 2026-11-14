"""Small framework-independent URL and localization utilities."""

from pathlib import Path
from urllib.parse import quote

from app_config import ASSET_DIR, DEFAULT_LANGUAGE
from content.site import COPY


def asset_url(filename: str) -> str:
    """Generate a cache-busted URL for a known flat asset filename."""
    if not filename or Path(filename).name != filename or filename in {'.', '..'} or '\\' in filename:
        raise ValueError('Asset filename must be a single relative path component')
    path = ASSET_DIR / filename
    version = path.stat().st_mtime_ns if path.is_file() else 0
    return f'/assets/{quote(filename, safe="")}?v={version}'


def normalized_language(lang: str | None) -> str:
    """Accept only the two languages supported by the portfolio."""
    language = (lang or DEFAULT_LANGUAGE).upper()
    return language if language in COPY else DEFAULT_LANGUAGE


def business_url(language: str) -> str:
    return f'/?lang={language}#business-solutions'


def localized(value: object, lang: str) -> str:
    """Select a localized research field without changing its scientific content."""
    if isinstance(value, dict):
        return str(value.get(lang) or value.get('en') or '')
    return '' if value is None else str(value)
