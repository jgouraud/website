"""Reusable portfolio cards and showcase section headings."""

from nicegui import ui

from app_config import ASSET_DIR
from utils import asset_url


def section_header(title: str, show_all: str, accessible_label: str, row_key: str) -> None:
    """Section headings stay visible when the other rows are folded away."""
    section_ids = {'business': 'business-solutions', 'research': 'research-papers',
                   'academic': 'academic-projects'}
    with ui.element('div').classes('section-header'):
        ui.html(title, tag='h2').classes('section-title')
        with ui.link(show_all, target=f'#{section_ids[row_key]}').classes('show-all').props(
            f'aria-label="{accessible_label}" aria-expanded="false" '
            f'data-showcase-toggle="{row_key}"'
        ):
            ui.icon('arrow_forward').props('aria-hidden=true')

def demo_card(title: str, description: str, illustration: str, alt: str,
              destination: str = '') -> None:
    """Business card with a compact banner that expands on hover/focus."""
    source = asset_url(illustration)
    with ui.card().props(
        f'flat tabindex=0 role=group aria-label="{title}: {description}"'
    ).classes('demo-card showcase-card' + (' demo-card-clickable' if destination else '')) as card:
        with ui.element('div').classes('demo-banner'):
            if (ASSET_DIR / illustration).is_file():
                ui.element('img').props(
                    f'src="{source}" alt="{alt}" width=1536 height=1024 decoding=async'
                ).classes('demo-illustration')
            else:
                with ui.element('div').classes('project-image-placeholder'):
                    ui.icon('dashboard_customize')
                    ui.label(title)
            if destination:
                with ui.link(target=destination).classes('circle-arrow demo-arrow').props(
                    f'aria-label="{title}" title="{title}"'
                ):
                    ui.icon('arrow_forward').props('aria-hidden=true')

    if destination:
        # Both mouse and keyboard can open the complete internal demo page.
        card.on('click', js_handler=(
            f'event => {{ if (!event.target.closest("a")) '
            f'window.location.assign("{destination}"); }}'
        ))
        card.on('keydown', js_handler=(
            f'event => {{ if ((event.key === "Enter" || event.key === " ") '
            f'&& event.target === event.currentTarget) {{ event.preventDefault(); '
            f'window.location.assign("{destination}"); }} }}'
        ))

def project_card(title: str, illustration: str, destination: str = '',
                 *, icon_name: str = 'school', fallback_label: str = '') -> None:
    """Title-only academic/research tile; illustration opens only on hover/focus."""
    with ui.card().props('flat').classes(
        'project-card showcase-card' + (' project-card-clickable' if destination else '')
    ):
        with ui.element('div').classes('project-bottom'):
            ui.label(title).classes('project-title')
            if destination:
                with ui.element('div').classes('circle-arrow'):
                    ui.icon('arrow_forward').props('aria-hidden=true')
        with ui.element('div').classes('project-image-reveal'):
            if (ASSET_DIR / illustration).is_file():
                ui.element('img').props(
                    f'src="{asset_url(illustration)}" alt="{title}" loading=lazy'
                ).classes('project-image')
            else:
                with ui.element('div').classes('project-image-placeholder'):
                    ui.icon(icon_name).props('aria-hidden=true')
                    ui.label(fallback_label or title)
        if destination:
            ui.link(target=destination).classes('project-card-overlay').props(
                f'aria-label="{title}" title="{title}"'
            )
