"""PartFinder's interactive search demo in the portfolio's shared solution layout."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import Request
from nicegui import ui

DEMO_DIR = Path(__file__).resolve().parents[2] / 'demos' / 'clip_search_minimal'
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from backend import register_backend, runtime  # noqa: E402
from app_config import ASSET_DIR, DEFAULT_LANGUAGE  # noqa: E402
from components.layout import setup_page, site_header  # noqa: E402
from components.partfinder_search import PartFinderSearch  # noqa: E402
from content.site import COPY, DEMO_IMAGES  # noqa: E402
from utils import asset_url, business_url, normalized_language  # noqa: E402


COPY_BY_LANGUAGE = {
    'EN': {
        'breadcrumb': 'Business solutions', 'kicker': 'Multimodal retrieval  •  computer vision',
        'title': 'Find mechanical parts from an image or a description.',
        'lead': 'PartFinder compares your query with a local, read-only catalog using a shared CLIP embedding model.',
        'summary_title': 'Search with the clues you have',
        'summary': 'Upload a reference image, describe the part, or combine both. The demo ranks visually similar catalog items without changing the shared model or collection.',
        'steps_title': 'How the demo works',
        'steps': [('Add a reference', 'Use a photo or a concise description of the part you need to identify.'),
                  ('Compare embeddings', 'The local CLIP model encodes only your query and compares it with catalog image vectors.'),
                  ('Review matches', 'Filter ranked results by classification and inspect each candidate in more detail.')],
        'example_title': 'Try it', 'example': 'Start with “A toothed gear that transmits rotation”, or upload a clear picture of one part.',
        'back': 'Back to business solutions',
    },
    'FR': {
        'breadcrumb': 'Solutions professionnelles', 'kicker': 'Recherche multimodale  •  vision par ordinateur',
        'title': 'Trouvez une pièce mécanique avec une image ou une description.',
        'lead': 'PartFinder compare votre requête à un catalogue local en lecture seule grâce à un modèle CLIP partagé.',
        'summary_title': 'Recherchez avec les indices disponibles',
        'summary': 'Importez une image de référence, décrivez la pièce ou combinez les deux. La démo classe les éléments visuellement proches sans modifier le modèle ni le catalogue partagé.',
        'steps_title': 'Fonctionnement de la démo',
        'steps': [('Ajoutez une référence', 'Utilisez une photo ou une description concise de la pièce à identifier.'),
                  ('Comparez les embeddings', 'Le modèle CLIP local encode votre requête et la compare aux vecteurs du catalogue.'),
                  ('Examinez les résultats', 'Filtrez les résultats par classification et consultez les candidats en détail.')],
        'example_title': 'À essayer', 'example': 'Commencez par « un engrenage denté qui transmet une rotation » ou importez une photo nette.',
        'back': 'Retour aux solutions professionnelles',
    },
}


def build_partfinder_page(language: str, is_dark: bool = False) -> None:
    t, site_copy = COPY_BY_LANGUAGE[language], COPY[language]
    image = next(filename for key, filename in DEMO_IMAGES if key == 'clip')
    dark_mode = setup_page(f"{site_copy['clip_title']} | Julien Gouraud", is_dark)
    site_header(language, dark_mode, path='/partfinder', selected_nav=1)
    with ui.element('main').classes('solution-page'):
        with ui.element('div').classes('solution-breadcrumb-row'):
            with ui.link(target=business_url(language)).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(t['breadcrumb'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(site_copy['clip_title'])
        with ui.element('section').classes('solution-art-banner'):
            with ui.element('div').classes('solution-art-inner'):
                with ui.element('div').classes('solution-visual-crop'):
                    if (ASSET_DIR / image).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(image)}" alt="{site_copy["clip_image_alt"]}" width=1536 height=1024 decoding=async'
                        ).classes('solution-visual-image')
                    else:
                        ui.label('Add the PartFinder illustration to assets/.').classes('solution-image-missing')
        with ui.element('aside').classes('solution-example partfinder-try-tip'):
            ui.icon('tips_and_updates').classes('solution-example-icon').props('aria-hidden=true')
            with ui.element('div'):
                ui.label(t['example_title']).classes('solution-example-title')
                ui.label(t['example']).classes('solution-example-copy')
        with ui.element('div').classes('solution-content'):
            with ui.element('section').classes('solution-status partfinder-demo'):
                ui.label(site_copy['clip_title']).classes('solution-project-label')
                ui.label(t['kicker']).classes('solution-kicker')
                ui.html(t['title'], tag='h1').classes('partfinder-title')
                ui.label(t['lead']).classes('partfinder-lead')
                PartFinderSearch(runtime, language)
            with ui.element('section'):
                ui.html(t['summary_title'], tag='h2').classes('solution-section-heading')
                ui.label(t['summary']).classes('solution-section-intro')
            with ui.element('section'):
                ui.html(t['steps_title'], tag='h2').classes('solution-section-heading')
                with ui.element('div').classes('solution-steps'):
                    for number, (title, copy) in enumerate(t['steps'], start=1):
                        with ui.element('div').classes('solution-step'):
                            ui.label(f'{number:02d}').classes('solution-step-number')
                            ui.label(title).classes('solution-step-title')
                            ui.label(copy).classes('solution-step-copy')
            with ui.element('div').classes('solution-actions'):
                ui.button(t['back'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(business_url(language))).props('no-caps unelevated').classes('solution-back')


@ui.page('/partfinder')
def partfinder_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_partfinder_page(normalized_language(lang), is_dark=request.cookies.get('portfolio_theme') == 'dark')
