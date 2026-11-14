"""Homepage with business, research, and academic showcases."""

from fastapi import Request
from nicegui import ui

from app_config import ASSET_DIR, DEFAULT_LANGUAGE, GITHUB_URL, LINKEDIN_URL
from components.cards import demo_card, project_card, section_header
from components.layout import setup_page, site_header
from content.research import RESEARCH_PROJECT
from content.site import COPY, DEMO_IMAGES, DEMO_ROUTES, PROJECT_IMAGES
from utils import localized, normalized_language


def build_homepage(language: str, is_dark: bool = False) -> None:
    t = COPY[language]
    dark_mode = setup_page('Julien Gouraud | AI Engineer', is_dark)
    ui.add_head_html('<script src="/scripts/showcase.js" defer></script>')
    site_header(language, dark_mode, path='/', selected_nav=0)

    with ui.element('section').classes('hero-shell').props('id=about'):
        with ui.element('div').classes('hero-inner'):
            with ui.element('div').classes('hero-copy'):
                ui.label(t['eyebrow']).classes('hero-eyebrow')
                ui.html(t['pitch'], tag='h1').classes('hero-pitch')
                with ui.element('div').classes('hero-actions'):
                    for label, url, style, icon in (
                        ('LinkedIn', LINKEDIN_URL, 'linkedin-button', 'linkedin'),
                        ('GitHub', GITHUB_URL, 'github-button', 'github'),
                    ):
                        if not url:
                            continue
                        button = ui.button(color=None).props('no-caps unelevated').classes(
                            f'social-button {style}'
                        )
                        with button:
                            ui.element('img').props(
                                f'src="/assets/{icon}.svg" alt="" aria-hidden="true"'
                            ).classes('social-icon')
                            ui.label(label)
                        if url:
                            button.props(f'href="{url}" target="_blank" rel="noopener noreferrer"')

            portrait = ASSET_DIR / 'portrait.png'
            if portrait.is_file():
                ui.image('/assets/portrait.png').classes('hero-portrait').bind_source_from(
                    dark_mode, 'value',
                    backward=lambda dark: '/assets/portrait-dark.png' if dark and
                    (ASSET_DIR / 'portrait-dark.png').is_file() else '/assets/portrait.png',
                )
            else:
                with ui.element('div').classes('portrait-placeholder'):
                    ui.icon('account_circle').classes('placeholder-icon')
                    ui.label(t['portrait_placeholder']).classes('placeholder-label')

    with ui.element('main').classes('main-content').props('data-active-row="all"'):
        # 1. Business solutions: three interactive demos.
        with ui.element('section').classes('explore-section showcase-section').props(
            'id=business-solutions data-showcase-row="business"'
        ):
            section_header(t['explore'], t['show_all'], t['show_all_business'], 'business')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('demos-grid'):
                        for key, filename in DEMO_IMAGES:
                            route = DEMO_ROUTES[key]
                            destination = f'{route}?lang={language}' if route else ''
                            demo_card(t[f'{key}_title'], t[f'{key}_description'], filename,
                                      t[f'{key}_image_alt'], destination)

        # 2. Research papers: independent middle row (no academic projects).
        with ui.element('section').classes('research-section showcase-section').props(
            'id=research-papers data-showcase-row="research"'
        ):
            section_header(t['research_heading'], t['show_all'], t['show_all_research'], 'research')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('projects-grid research-grid'):
                        project_card(
                            t['research_project_title'], RESEARCH_PROJECT['banner_illustration'],
                            f'/convex-deepstack?lang={language}', icon_name='psychology',
                            fallback_label=localized(RESEARCH_PROJECT['domain'], language.lower()),
                        )

        # 3. Academic projects only, each collapsed to its title at rest.
        with ui.element('section').classes('projects-section showcase-section').props(
            'id=academic-projects data-showcase-row="academic"'
        ):
            section_header(t['featured'], t['show_all'], t['show_all_academic'], 'academic')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('projects-grid'):
                        academic_icons = ('directions_car', 'monitor_heart', 'rocket_launch', 'precision_manufacturing')
                        for index, (img, title) in enumerate(zip(PROJECT_IMAGES, t['projects'])):
                            destination = (f'/eeg?lang={language}' if index == 1 else
                                           f'/ball-valve?lang={language}' if index == 3 else '')
                            project_card(title, img, destination,
                                         icon_name=academic_icons[index])


@ui.page('/')
def index(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_homepage(normalized_language(lang), is_dark=request.cookies.get('portfolio_theme') == 'dark')
