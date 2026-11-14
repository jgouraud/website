"""Portfolio presentation for the existing PartFinder search backend."""

from __future__ import annotations

import base64
from io import BytesIO
import math

from nicegui import events, run, ui
from PIL import Image

from search_engine.errors import visitor_error
from search_engine.images import preview_url
from search_engine.ranking import Result, SCORE_LABELS
from search_engine.runtime import SearchRuntime, SearchSession
from search_engine.translation import translate_to_english
from search_engine.validation import MAX_IMAGE_BYTES, MAX_TEXT_CHARACTERS, read_reference_image


PAGE_SIZE = 12

UI_COPY = {
    'EN': {'query': 'Your query', 'starting': 'Starting search engine...', 'reference_image': 'Reference image',
           'upload': 'Drop an image or choose a file', 'remove_image': 'Remove image', 'or': 'OR',
           'describe': 'Describe the part', 'description': 'Text description',
           'placeholder': 'Shape, part family, distinctive features...', 'search': 'Search',
           'preparing': 'Preparing the search engine...', 'results': 'Search results', 'reset': 'Reset',
           'all_classifications': 'All classifications', 'classification': 'Classification',
           'ready': 'Ready to search', 'ready_help': 'Add an image or a description to find similar parts.',
           'unavailable': 'Search unavailable', 'image_ready': 'Image ready. Search with the image alone or add a description.',
           'translating': 'Detecting the query language and translating to English...',
           'comparing': 'Comparing your query with the collection...', 'no_matches': 'No matching parts',
           'refine': 'Try another classification or refine your query.', 'details': 'Details', 'close_details': 'Close details',
           'parts': 'parts', 'tips': 'Search tips', 'tips_text': 'Use one centered part in an image, or describe its shape and distinctive features.',
           'got_it': 'Got it', 'examples': [('Gear', 'A toothed gear that transmits rotation'), ('Washer', 'A thin flat ring with a central hole'), ('Fastener', 'A threaded screw or bolt')],
           'scores': {'global': 'Combined', 'image': 'Image to image', 'text_to_image': 'Text to image'}},
    'FR': {'query': 'Votre recherche', 'starting': 'Demarrage du moteur de recherche...', 'reference_image': 'Image de reference',
           'upload': 'Deposez une image ou choisissez un fichier', 'remove_image': 'Supprimer l image', 'or': 'OU',
           'describe': 'Decrivez la piece', 'description': 'Description textuelle',
           'placeholder': 'Forme, famille de pieces, caracteristiques distinctives...', 'search': 'Rechercher',
           'preparing': 'Preparation du moteur de recherche...', 'results': 'Resultats de recherche', 'reset': 'Reinitialiser',
           'all_classifications': 'Toutes les classifications', 'classification': 'Classification',
           'ready': 'Pret pour la recherche', 'ready_help': 'Ajoutez une image ou une description pour trouver des pieces similaires.',
           'unavailable': 'Recherche indisponible', 'image_ready': 'Image prete. Recherchez avec l image seule ou ajoutez une description.',
           'translating': 'Detection de la langue et traduction en anglais...',
           'comparing': 'Comparaison de votre recherche avec la collection...', 'no_matches': 'Aucune piece correspondante',
           'refine': 'Essayez une autre classification ou precisez votre recherche.', 'details': 'Details', 'close_details': 'Fermer les details',
           'parts': 'pieces', 'tips': 'Conseils de recherche', 'tips_text': 'Utilisez une piece centree dans l image ou decrivez sa forme et ses caracteristiques distinctives.',
           'got_it': 'Compris', 'examples': [('Engrenage', 'Un engrenage dente qui transmet une rotation'), ('Rondelle', 'Un anneau plat et mince avec un trou central'), ('Fixation', 'Une vis ou un boulon filete')],
           'scores': {'global': 'Combine', 'image': 'Image vers image', 'text_to_image': 'Texte vers image'}},
}


def _image_data_url(image: Image.Image) -> tuple[bytes, str]:
    output = BytesIO()
    image.save(output, format='PNG')
    data = output.getvalue()
    return data, 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')


class PartFinderSearch:
    """A per-visitor query form using the demo's shared, preloaded runtime."""

    def __init__(self, runtime: SearchRuntime, language: str = 'EN') -> None:
        self.runtime = runtime
        self.t = UI_COPY.get(language, UI_COPY['EN'])
        self.session = SearchSession(runtime)
        self.image_data: bytes | None = None
        self.results: list[Result] = []
        self.busy = self.catalog_loaded = self.has_searched = False
        self.classifications: list[str] = []
        self.results_panel = None
        self._build()
        self.ready_timer = ui.timer(.25, self.sync_runtime)
        self.sync_runtime()

    def _build(self) -> None:
        with ui.element('div').classes('partfinder-search-workspace query-only') as self.workspace:
            with ui.element('section').classes('query-panel'):
                with ui.element('div').classes('panel-heading'):
                    with ui.element('div').classes('query-heading-title'):
                        ui.html(self.t['query'], tag='h2')
                        with ui.element('div').classes('ready-pill').props('role=status aria-live=polite'):
                            self.ready_dot = ui.element('span').classes('ready-dot')
                            self.ready_label = ui.label('Starting search engine…')
                    ui.button(icon='info_outline', on_click=self.show_help, color=None).props(
                        'flat round dense aria-label="Search tips"').classes('small-button')
                with ui.element('div').classes('field-heading'):
                    ui.icon('add_photo_alternate')
                    ui.label(self.t['reference_image'])
                self.upload = ui.upload(label=self.t['upload'], auto_upload=True,
                    max_file_size=MAX_IMAGE_BYTES, max_files=1, on_upload=self.on_upload,
                    on_rejected=lambda: ui.notify('Choose a PNG, JPG, or WEBP under 12 MB.', type='warning')) \
                    .props('accept=.png,.jpg,.jpeg,.webp flat no-thumbnails add-icon=add_photo_alternate').classes('image-drop')
                self.preview = ui.image().props('fit=contain').classes('image-preview')
                self.preview.set_visibility(False)
                self.upload_help = ui.label('PNG, JPG, WEBP · up to 12 MB').classes('upload-help')
                with ui.element('div').classes('image-actions') as self.image_actions:
                    self.file_label = ui.label('').classes('file-name')
                    ui.button(icon='close', on_click=self.clear_image, color=None).props(
                        'flat aria-label="Remove image"').classes('small-button')
                self.image_actions.set_visibility(False)
                with ui.element('div').classes('query-divider').props('role=separator aria-label="Image or text"'):
                    ui.label(self.t['or'])
                with ui.element('div').classes('field-heading'):
                    ui.icon('edit_note')
                    ui.label(self.t['describe'])
                self.description = ui.textarea('Text description', placeholder='Shape, part family, distinctive features…') \
                    .props(f'outlined dense rows=3 maxlength={MAX_TEXT_CHARACTERS}').classes('description')
                self.description.props(f'label="{self.t["description"]}" placeholder="{self.t["placeholder"]}"')
                self.description.on_value_change(self.update_search_button)
                self.description.on('keydown', self.search, js_handler='''event => {
                    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); emit(); }
                }''')
                with ui.element('div').classes('examples'):
                    for label, text in self.t['examples']:
                        ui.button(label, on_click=lambda text=text: self.use_example(text), color=None).props(
                            'flat').classes('example-button')
                self.search_button = ui.button(self.t['search'], icon='search', on_click=self.search, color=None).props(
                    'unelevated').classes('search-button')
                self.search_button.disable()
                self.status = ui.label('Preparing the search engine…').classes('query-status').props(
                    'role=status aria-live=polite')

    def _build_results_panel(self) -> None:
        with ui.element('section').classes('results-pane') as self.results_panel:
            with ui.element('div').classes('results-heading'):
                with ui.element('div'):
                    ui.html(self.t['results'], tag='h2')
                    self.result_summary = ui.label('').classes('catalog-count')
                self.reset_button = ui.button(self.t['reset'], icon='restart_alt', on_click=self.reset_all, color=None).props(
                    'flat').classes('reset-button')
            with ui.element('div').classes('filter-bar'):
                options = {'': self.t['all_classifications'], **{key: key.replace('_', ' ').capitalize() for key in self.classifications}}
                self.classification = ui.select(options, value='', label=self.t['classification']).props('outlined dense options-dense')
                self.classification.on_value_change(self.apply_filters)
            with ui.element('div').classes('results-scroll') as self.scroll:
                self.results_grid = ui.element('div').classes('results-grid')
            with ui.element('div').classes('results-bottom'):
                self.range_label = ui.label('').classes('range-label')
                self.pagination = ui.pagination(min=1, max=1, value=1, direction_links=True,
                    on_change=self.render_page).props('dense max-pages=5 size=sm')

    def sync_runtime(self) -> None:
        if self.runtime.collection is not None and not self.catalog_loaded:
            self.classifications = sorted(set(self.runtime.collection.classifications) - {''})
            self.catalog_loaded = True
        if self.runtime.ready:
            self.ready_dot.classes(add='ready', remove='failed')
            self.ready_label.set_text(self.t['ready'])
            self.status.set_text(self.t['ready_help'])
            self.update_search_button()
            self.ready_timer.deactivate()
        elif self.runtime.error:
            self.ready_dot.classes(add='failed', remove='ready')
            self.ready_label.set_text(self.t['unavailable'])
            self.status.set_text(self.runtime.error)
            self.ready_timer.deactivate()

    def update_search_button(self) -> None:
        self.search_button.set_enabled(self.runtime.ready and not self.busy and bool(
            (self.description.value or '').strip() or self.image_data))

    def use_example(self, text: str) -> None:
        if not self.busy:
            self.description.set_value(text)
            self.update_search_button()

    async def on_upload(self, event: events.UploadEventArguments) -> None:
        try:
            image = await run.io_bound(read_reference_image, await event.file.read())
            self.image_data, source = _image_data_url(image)
            self.preview.set_source(source)
            self.preview.set_visibility(True)
            self.image_actions.set_visibility(True)
            self.upload.set_visibility(False)
            self.upload_help.set_visibility(False)
            self.file_label.set_text(event.file.name)
            self.status.set_text(self.t['image_ready'])
            self.update_search_button()
        except Exception as exc:
            ui.notify(visitor_error(exc, 'image upload'), type='negative')
        finally:
            event.sender.reset()

    def clear_image(self) -> None:
        if self.busy:
            return
        self.image_data = None
        self.preview.set_visibility(False)
        self.image_actions.set_visibility(False)
        self.upload.set_visibility(True)
        self.upload_help.set_visibility(True)
        self.update_search_button()

    async def search(self) -> None:
        if self.busy or not self.runtime.ready or not ((self.description.value or '').strip() or self.image_data):
            return
        self.busy = True
        self.search_button.props('loading')
        self.status.set_text('Comparing your query with the collection…')
        try:
            query = self.description.value or ''
            if query.strip():
                self.status.set_text(self.t['translating'])
                english_query = await run.io_bound(translate_to_english, query)
                if english_query != query.strip():
                    self.description.set_value(english_query)
                query = english_query
                self.status.set_text(self.t['comparing'])
            await self.runtime.submit_query(self.session, query, self.image_data)
            if not self.has_searched:
                with self.workspace:
                    self._build_results_panel()
                self.has_searched = True
                self.workspace.classes(remove='query-only')
            self.apply_filters()
            self.status.set_text('')
        except Exception as exc:
            self.status.set_text(visitor_error(exc, 'search'))
        finally:
            self.busy = False
            self.search_button.props(remove='loading')
            self.update_search_button()

    def apply_filters(self) -> None:
        self.results = self.session.results(self.classification.value or '')
        self.pagination.max = max(1, math.ceil(len(self.results) / PAGE_SIZE))
        self.pagination.set_value(1)
        self.pagination.update()
        self.render_page()

    def render_page(self) -> None:
        start = ((self.pagination.value or 1) - 1) * PAGE_SIZE
        visible = self.results[start:start + PAGE_SIZE]
        self.results_grid.clear()
        with self.results_grid:
            if not visible:
                with ui.element('div').classes('empty-state'):
                    ui.icon('manage_search')
                    ui.label(self.t['no_matches'])
                    ui.label(self.t['refine']).classes('micro-label')
            for index, result in enumerate(visible, start=start + 1):
                self.render_card(result, index)
        self.range_label.set_text(f'{start + 1}–{start + len(visible)} of {len(self.results)}' if visible else '0 parts')
        self.range_label.set_text(
            f'{start + 1}-{start + len(visible)} / {len(self.results)}' if visible else f'0 {self.t["parts"]}'
        )
        self.pagination.set_visibility(len(self.results) > PAGE_SIZE)

    def render_card(self, result: Result, index: int) -> None:
        with ui.element('article').classes('catalog-card'):
            source = preview_url(result.image_path)
            if source:
                ui.image(source).props('fit=contain').classes('part-image')
            else:
                ui.icon('image_not_supported').classes('part-image')
            with ui.element('div').classes('part-content'):
                with ui.element('div').classes('part-topline'):
                    ui.label(result.name).classes('part-title')
                    ui.label(f'{index:02}').classes('part-rank')
                ui.label(f'ID {result.item_id}').classes('part-id')
                if result.classification:
                    ui.label(result.classification.replace('_', ' ')).classes('class-tag')
                ui.button(self.t['details'], icon='open_in_full', on_click=lambda: self.show_details(result), color=None).props(
                    'flat dense').classes('detail-button')

    def show_details(self, result: Result) -> None:
        with ui.dialog() as dialog, ui.card().classes('partfinder-detail-dialog'):
            with ui.row().classes('w-full items-center justify-between'):
                ui.label(result.name).classes('detail-title')
                ui.button(icon='close', on_click=dialog.close, color=None).props('flat round dense aria-label="Close details"')
            ui.label(f'ID {result.item_id} · {result.classification.replace("_", " ")}').classes('micro-label')
            if source := preview_url(result.image_path):
                ui.image(source).props('fit=contain').classes('detail-image')
            for key, label in SCORE_LABELS.items():
                value = result.scores.get(key, float('nan'))
                if math.isfinite(value):
                    ui.label(f'{self.t["scores"][key]}: {100 * value:.1f}%').classes('micro-label')
        dialog.open()

    def reset_all(self) -> None:
        self.session.reset()
        self.results = []
        self.has_searched = False
        self.results_panel.delete()
        self.results_panel = None
        self.workspace.classes(add='query-only')
        self.description.set_value('')
        self.clear_image()
        self.status.set_text(self.t['ready_help'])

    def show_help(self) -> None:
        with ui.dialog() as dialog, ui.card().classes('partfinder-detail-dialog'):
            ui.label(self.t['tips']).classes('detail-title')
            ui.label(self.t['tips_text']).classes('detail-description')
            ui.button(self.t['got_it'], on_click=dialog.close).props('unelevated no-caps')
        dialog.open()
