"""Ball-valve predictive maintenance academic project route."""

from fastapi import Request
from nicegui import ui

from app_config import ASSET_DIR, DEFAULT_LANGUAGE
from components.layout import setup_page, site_header
from content.ball_valve import BALL_VALVE_PROJECT, BALL_VALVE_TEXT
from utils import asset_url, localized, normalized_language


def render_ball_valve_content(lang: str, academic_url: str) -> None:
    """Render the ball-valve project using the same components as the EEG page."""
    t = BALL_VALVE_TEXT[lang]
    project = BALL_VALVE_PROJECT
    project_title = localized(project['title'], lang)

    with ui.element('main').classes('eeg-page ball-valve-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=academic_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(t['academic'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['academic_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(localized(project['domain'], lang))
                    ui.html(project_title, tag='h1').classes('eeg-title')
                    ui.label(localized(project['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        if (ASSET_DIR / 'CIVIL426_Final_Project_Report.pdf').is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(project['report_url'], new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label(t['missing_report']).classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner = project['banner_illustration']
                    if (ASSET_DIR / banner).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(banner)}" alt="Hydropower ball valve and sensor anomaly illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('precision_manufacturing').classes('eeg-visual-icon')
                            ui.label('HYDROPOWER  ·  AI').classes('eeg-visual-caption')

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
                for key, icon in (('overview', 'device_hub'), ('methodology', 'timeline')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(localized(project[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('groups').props('aria-hidden=true')
                        ui.html(t['contribution'], tag='h2').classes('eeg-card-title')
                    ui.label(localized(project['contribution'], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('insights').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(project['key_result']['value']).classes('eeg-result-value')
                            ui.label(localized(project['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(localized(project['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure = project['figure_file']
                            if (ASSET_DIR / figure).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure)}" alt="Test-set fault clustering and distribution across fault classes" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(t['figure']).classes('eeg-figure-caption')
                            else:
                                # Never invent a benchmark when the sourced figure is absent.
                                ui.label(t['figure']).classes('eeg-figure-caption')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(t['academic'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(academic_url)) \
                    .props('no-caps unelevated').classes('eeg-back-button')

def build_ball_valve_page(language: str, is_dark: bool = False) -> None:
    """CIVIL-426 detail, embedded in the main NiceGUI site and its shared theme."""
    project_title = localized(BALL_VALVE_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    site_header(language, dark_mode, path='/ball-valve', selected_nav=2)
    render_ball_valve_content(language.lower(), academic_url=f'/?lang={language}#academic-projects')


@ui.page('/ball-valve')
def ball_valve_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_ball_valve_page(normalized_language(lang),
                          is_dark=request.cookies.get('portfolio_theme') == 'dark')
