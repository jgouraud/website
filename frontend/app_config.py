"""Shared filesystem paths and user-facing configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / 'assets'
STYLES_DIR = ROOT / 'styles'
SCRIPTS_DIR = ROOT / 'scripts'
DEFAULT_LANGUAGE = 'EN'
LINKEDIN_URL = 'https://www.linkedin.com/in/julien-gouraud-5783962b8'
# A real GitHub profile URL can be set when available; no broken link is rendered.
GITHUB_URL = ''
