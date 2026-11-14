"""Site-wide theme, navigation, and page head setup."""

from typing import Any

from nicegui import ui

from content.site import COPY, NAV_ICONS
from utils import business_url


STYLESHEETS = ('base.css', 'showcase.css', 'solutions.css', 'details.css', 'partfinder.css')


def setup_page(title: str, is_dark: bool) -> Any:
    """Load separate CSS files and initialize per-page presentation state."""
    ui.page_title(title)
    ui.colors(primary='#0c68cf')
    for stylesheet in STYLESHEETS:
        ui.add_head_html(f'<link rel="stylesheet" href="/styles/{stylesheet}">')
    return ui.dark_mode(is_dark)


def site_header(language: str, dark_mode: Any, *, path: str = '/', selected_nav: int = 0) -> None:
    """Shared branding, working home/back navigation and persistent theme and language."""
    t = COPY[language]
    with ui.element('header').classes('site-header'):
        with ui.element('div').classes('header-inner'):
            with ui.element('div').classes('brand'):
                ui.label('JG').classes('brand-mark')
                ui.element('span').classes('brand-divider')
                ui.label('Julien Gouraud').classes('brand-name')

            with ui.element('nav').classes('nav-links'):
                for index, (icon, label) in enumerate(zip(NAV_ICONS, t['nav'])):
                    destination = (f'/?lang={language}' if index == 0 else
                                   business_url(language) if index == 1 else
                                   f'/?lang={language}#academic-projects' if index == 2 else
                                   f'/?lang={language}#research-papers' if index == 3 else
                                   f'/about?lang={language}')
                    showcase_row = ({0: 'all', 1: 'business', 2: 'academic', 3: 'research'}.get(index)
                                    if path == '/' else None)
                    kwargs = ({'on_click': lambda to=destination: ui.navigate.to(to)}
                              if destination and showcase_row is None else {})
                    button = ui.button(label, icon=icon, color=None, **kwargs).props(
                        'flat no-caps' + (f' data-showcase-nav={showcase_row}' if showcase_row else '')
                    ).classes(
                        'nav-link' + (' active' if index == selected_nav else '')
                    )
                    if showcase_row:
                        button.on('click', js_handler=(
                            f"event => window.portfolioShowcase?.select('{showcase_row}')"
                        ))

            with ui.element('div').classes('header-controls'):
                with ui.element('div').classes('language-switch').props('role=group aria-label=Language'):
                    for lang in ('EN', 'FR'):
                        ui.button(lang, on_click=lambda choice=lang: ui.navigate.to(
                            f'{path}?lang={choice}'
                        ), color=None).props(
                            f'flat no-caps aria-pressed={str(language == lang).lower()}'
                        ).classes('lang-button' + (' selected' if language == lang else ''))

                def toggle_theme() -> None:
                    dark_mode.toggle()
                    theme = 'dark' if dark_mode.value else 'light'
                    ui.run_javascript(
                        f'document.cookie = "portfolio_theme={theme}; Path=/; Max-Age=31536000; SameSite=Lax"'
                    )
                    label = t['light_theme' if dark_mode.value else 'dark_theme']
                    theme_button.props(
                        f'aria-pressed={str(dark_mode.value).lower()} aria-label="{label}" title="{label}"'
                    )

                theme_label = t['light_theme' if dark_mode.value else 'dark_theme']
                theme_button = ui.button(on_click=toggle_theme, color=None).props(
                    f'flat round aria-pressed={str(dark_mode.value).lower()} '
                    f'aria-label="{theme_label}" title="{theme_label}"'
                ).classes('theme-toggle').bind_icon_from(
                    dark_mode, 'value', backward=lambda dark: 'light_mode' if dark else 'dark_mode'
                )
