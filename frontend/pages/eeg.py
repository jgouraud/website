"""EEG seizure-detection academic project route."""

from pathlib import Path
from typing import Callable

from fastapi import Request
from nicegui import ui

from app_config import ASSET_DIR, DEFAULT_LANGUAGE
from components.layout import setup_page, site_header
from content.eeg import EEG_PROJECT, EEG_TEXT
from utils import asset_url, localized, normalized_language


def render_eeg_content(lang: str, assets_dir: Path, asset_url: Callable[[str], str],
                       academic_url: str) -> None:
    """Render the EEG project with shared site styling and cache-busted assets.

    Missing optional imagery, figures and reports use explicit fallbacks.
    """
    t = EEG_TEXT[lang]
    project_title = localized(EEG_PROJECT['title'], lang)
    back_text = t['academic']
    missing_report = ('Le rapport sera disponible après ajout du PDF.' if lang == 'fr'
                      else 'The report link will appear when the PDF is added.')

    with ui.element('main').classes('eeg-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=academic_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(back_text)
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['academic_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(localized(EEG_PROJECT['domain'], lang))
                    ui.html(project_title, tag='h1').classes('eeg-title')
                    ui.label(localized(EEG_PROJECT['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        report_file = assets_dir / EEG_PROJECT['report_url'].rsplit('/', 1)[-1]
                        if report_file.is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(EEG_PROJECT['report_url'], new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label(missing_report).classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner_name = next((name for name in (EEG_PROJECT['banner_illustration'], 'eeg-decoding.svg')
                                        if (assets_dir / name).is_file()), None)
                    if banner_name:
                        ui.element('img').props(
                            f'src="{asset_url(banner_name)}" alt="EEG signal analysis illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('monitor_heart').classes('eeg-visual-icon')
                            ui.label('EEG  ·  AI').classes('eeg-visual-caption')

        with ui.element('div').classes('eeg-container eeg-content'):
            with ui.element('section').classes('eeg-panel eeg-skills-panel'):
                with ui.element('div').classes('eeg-section-header'):
                    ui.html(t['skills'], tag='h2').classes('eeg-section-heading')
                    ui.element('span').classes('eeg-section-rule')
                with ui.element('div').classes('eeg-skill-tags'):
                    for skill in EEG_PROJECT['skills']:
                        with ui.element('div').classes('eeg-skill-tag'):
                            ui.icon(skill['icon']).props('aria-hidden=true')
                            ui.label(localized(skill, lang))

            with ui.element('div').classes('eeg-details'):
                for key, icon in (('overview', 'device_hub'), ('methodology', 'gps_fixed')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(localized(EEG_PROJECT[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('table_chart').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(EEG_PROJECT['key_result']['value']).classes('eeg-result-value')
                            ui.label(localized(EEG_PROJECT['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(localized(EEG_PROJECT['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure_filename = EEG_PROJECT['figure']['file']
                            if (assets_dir / figure_filename).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure_filename)}" alt="ROC AUC model comparison" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(localized(EEG_PROJECT['figure']['caption'], lang)).classes('eeg-figure-caption')
                            else:
                                # Show only the sourced best-model ROC AUC. Do not invent other model metrics.
                                ui.label('ROC AUC').classes('eeg-meter-title')
                                score = EEG_PROJECT['key_result']['value']
                                ui.element('progress').classes('eeg-meter-track').props(
                                    f'value="{score}" max="1" aria-label="ROC AUC {score} out of 1"'
                                )
                                with ui.element('div').classes('eeg-meter-axis'):
                                    ui.label('0.0')
                                    ui.label('1.0')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(back_text, icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(academic_url)).props(
                    'no-caps unelevated'
                ).classes('eeg-back-button')

def build_eeg_page(language: str, is_dark: bool = False) -> None:
    """EEG research detail: main-site style, language, navigation, and theme."""
    project_title = localized(EEG_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    site_header(language, dark_mode, path='/eeg', selected_nav=2)
    render_eeg_content(language.lower(), ASSET_DIR, asset_url,
                       academic_url=f'/?lang={language}#academic-projects')


@ui.page('/eeg')
def eeg_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_eeg_page(normalized_language(lang),
                   is_dark=request.cookies.get('portfolio_theme') == 'dark')
