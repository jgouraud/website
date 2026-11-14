"""Flowdesk business solution route."""

from fastapi import Request
from nicegui import ui

from app_config import DEFAULT_LANGUAGE
from components.business_solution import build_solution_page
from utils import normalized_language


@ui.page('/flowdesk')
def flowdesk_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_solution_page('flowdesk', normalized_language(lang),
                        is_dark=request.cookies.get('portfolio_theme') == 'dark')
