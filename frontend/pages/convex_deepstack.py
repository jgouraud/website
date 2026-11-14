"""Convex DeepStack research paper route."""

from fastapi import Request
from nicegui import ui

from app_config import ASSET_DIR, DEFAULT_LANGUAGE
from components.layout import setup_page, site_header
from content.research import RESEARCH_PROJECT, RESEARCH_TEXT
from utils import asset_url, localized, normalized_language


def render_research_content(lang: str, research_url: str) -> None:
    """Render Convex DeepStack with the same components as the academic detail pages."""
    t = RESEARCH_TEXT[lang]
    project = RESEARCH_PROJECT
    title = localized(project['title'], lang)

    with ui.element('main').classes('eeg-page research-detail-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=research_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(t['research'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['research_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(localized(project['domain'], lang))
                    ui.html(title, tag='h1').classes('eeg-title')
                    ui.label(localized(project['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        report = project['report_url']
                        if (ASSET_DIR / report.rsplit('/', 1)[-1]).is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(report, new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label('Article PDF à ajouter au dossier assets/.' if lang == 'fr'
                                     else 'Paper PDF will be linked once added to assets/.').classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner = project['banner_illustration']
                    if (ASSET_DIR / banner).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(banner)}" alt="Convex DeepStack research illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('psychology').classes('eeg-visual-icon')
                            ui.label('CONVEX DEEPSTACK').classes('eeg-visual-caption')

        with ui.element('div').classes('eeg-container eeg-content'):
            with ui.element('section').classes('eeg-panel eeg-skills-panel'):
                with ui.element('div').classes('eeg-section-header'):
                    ui.html(t['skills'], tag='h2').classes('eeg-section-heading')
                    ui.element('span').classes('eeg-section-rule')
                with ui.element('div').classes('eeg-skill-tags'):
                    for skill in project['skills']:
                        with ui.element('div').classes('eeg-skill-tag'):
                            ui.icon(skill['icon']).props('aria-hidden=true')
                            ui.label(localized(skill, lang))

            with ui.element('div').classes('eeg-details'):
                for key, icon_name in (('overview', 'device_hub'), ('methodology', 'gps_fixed')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon_name).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(localized(project[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('table_chart').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(project['key_result']['value']).classes('eeg-result-value')
                            ui.label(localized(project['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(localized(project['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure = project['figure']['file']
                            if (ASSET_DIR / figure).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure)}" alt="Prediction error versus search time" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(localized(project['figure']['caption'], lang)).classes('eeg-figure-caption')
                            else:
                                with ui.element('div').classes('eeg-visual-fallback research-figure-fallback'):
                                    ui.icon('insights').classes('eeg-visual-icon')
                                    ui.label(localized(project['figure']['caption'], lang)).classes('eeg-figure-caption')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(t['research'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(research_url)).props(
                    'no-caps unelevated'
                ).classes('eeg-back-button')

def build_research_page(language: str, is_dark: bool = False) -> None:
    project_title = localized(RESEARCH_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    site_header(language, dark_mode, path='/convex-deepstack', selected_nav=3)
    render_research_content(language.lower(), research_url=f'/?lang={language}#research-papers')


@ui.page('/convex-deepstack')
def convex_deepstack_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_research_page(normalized_language(lang),
                        is_dark=request.cookies.get('portfolio_theme') == 'dark')
