"""Bilingual About page for the portfolio."""

from fastapi import Request
from nicegui import ui

from app_config import DEFAULT_LANGUAGE
from components.layout import setup_page, site_header
from content.site import COPY
from utils import normalized_language


def build_about_page(language: str, is_dark: bool = False) -> None:
    """Render the personal background, work, and interests page."""
    copy = COPY[language]['about']
    dark_mode = setup_page('Julien Gouraud | About', is_dark)
    site_header(language, dark_mode, path='/about', selected_nav=4)

    with ui.element('main').classes('about-page'):
        with ui.element('section').classes('about-section'):
            ui.label(copy['journey_title']).classes('about-section-title')
            with ui.element('article').classes('about-content-card'):
                for paragraph in copy['journey']:
                    ui.label(paragraph).classes('about-copy')

        with ui.element('section').classes('about-section about-work-section'):
            ui.label(copy['work_title']).classes('about-section-title')
            with ui.element('article').classes('about-content-card'):
                for paragraph in copy['work']:
                    ui.label(paragraph).classes('about-copy')

        with ui.element('section').classes('about-section'):
            ui.label(copy['beyond_title']).classes('about-section-title')
            with ui.element('div').classes('about-interests'):
                for icon, title, paragraph in (
                    ('terrain', copy['hiking_title'], copy['hiking']),
                    ('restaurant', copy['cooking_title'], copy['cooking']),
                ):
                    with ui.element('article').classes('interest-card'):
                        ui.icon(icon).classes('interest-icon')
                        ui.label(title).classes('interest-title')
                        ui.label(paragraph).classes('interest-copy')

        ui.label(copy['values']).classes('about-values')


@ui.page('/about')
def about(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_about_page(normalized_language(lang), is_dark=request.cookies.get('portfolio_theme') == 'dark')
