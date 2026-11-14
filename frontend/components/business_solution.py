"""Shared renderer for business solution pages (planned demo, not a working product)."""

from nicegui import ui

from app_config import ASSET_DIR
from components.layout import setup_page, site_header
from content.site import COPY, DEMO_IMAGES, DEMO_ROUTES
from content.solutions import PAGE_LABELS, SOLUTION_COPY
from utils import asset_url, business_url


def build_solution_page(key: str, language: str, is_dark: bool = False) -> None:
    """Show project-specific information without pretending the demo is finished."""
    project_title = COPY[language][f'{key}_title']
    project_alt = COPY[language][f'{key}_image_alt']
    project_image = next(image for image_key, image in DEMO_IMAGES if image_key == key)
    t = SOLUTION_COPY[key][language]
    labels = PAGE_LABELS[language]
    path = DEMO_ROUTES[key]
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    site_header(language, dark_mode, path=path, selected_nav=1)

    with ui.element('main').classes('solution-page'):
        with ui.element('div').classes('solution-breadcrumb-row'):
            with ui.link(target=business_url(language)).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(labels['breadcrumb'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        # The original illustration is the ONLY top banner (source y=0..416).
        with ui.element('section').classes('solution-art-banner'):
            with ui.element('div').classes('solution-art-inner'):
                with ui.element('div').classes('solution-visual-crop'):
                    if (ASSET_DIR / project_image).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(project_image)}" alt="{project_alt}" '
                            'width=1536 height=1024 decoding=async'
                        ).classes('solution-visual-image')
                    else:
                        ui.label(labels['missing_art']).classes('solution-image-missing')

        with ui.element('div').classes('solution-content'):
            # The large status panel is the page's main component.
            with ui.element('section').classes('solution-status').props('role=status'):
                with ui.element('div').classes('solution-status-inner'):
                    ui.label(project_title).classes('solution-project-label')
                    ui.label(t['kicker']).classes('solution-kicker')
                    with ui.element('div').classes('solution-status-icon'):
                        ui.icon('construction').props('aria-hidden=true')
                    ui.html(labels['status_title'], tag='h1').classes('solution-status-title')
                    ui.label(labels['status_soon']).classes('solution-coming')
                    ui.label(labels['status_note']).classes('solution-status-note')
                    ui.label(t['lead']).classes('solution-status-lead')

            with ui.element('section'):
                ui.html(t['summary_title'], tag='h2').classes('solution-section-heading')
                ui.label(t['summary']).classes('solution-section-intro')

            with ui.element('section'):
                ui.html(t['steps_title'], tag='h2').classes('solution-section-heading')
                with ui.element('div').classes('solution-steps'):
                    for number, (step_title, step_copy) in enumerate(t['steps'], start=1):
                        with ui.element('div').classes('solution-step'):
                            ui.label(f'{number:02d}').classes('solution-step-number')
                            ui.label(step_title).classes('solution-step-title')
                            ui.label(step_copy).classes('solution-step-copy')

            with ui.element('aside').classes('solution-example'):
                ui.icon('insights').classes('solution-example-icon').props('aria-hidden=true')
                with ui.element('div'):
                    ui.label(t['example_title']).classes('solution-example-title')
                    ui.label(t['example']).classes('solution-example-copy')

            with ui.element('div').classes('solution-actions'):
                ui.button(labels['back'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(business_url(language))).props(
                    'no-caps unelevated'
                ).classes('solution-back')
