"""Smoke-check every page with a minimal UI boundary double.

This checks our page composition and data access, not NiceGUI's rendering internals.
A browser/E2E run is still required with the NiceGUI package installed.
"""

import importlib
import sys
from types import ModuleType, SimpleNamespace


class UIElement:
    def __init__(self, *, value=False):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def props(self, *_args, **_kwargs):
        return self

    def classes(self, *_args, **_kwargs):
        return self

    def style(self, *_args, **_kwargs):
        return self

    def on(self, *_args, **_kwargs):
        return self

    def on_value_change(self, *_args, **_kwargs):
        return self

    def bind_icon_from(self, *_args, **_kwargs):
        return self

    def bind_source_from(self, *_args, **_kwargs):
        return self

    def set_visibility(self, *_args, **_kwargs):
        return self

    def set_enabled(self, *_args, **_kwargs):
        return self

    def disable(self):
        return self

    def deactivate(self):
        return self

    def toggle(self):
        self.value = not self.value


class FakeUI:
    def __init__(self):
        self.routes = {}
        self.labels = []
        self.page_titles = []
        self.started = False
        self.navigate = SimpleNamespace(to=lambda *_args, **_kwargs: None)

    def page(self, path):
        def register(view):
            self.routes[path] = view
            return view
        return register

    def label(self, value=''):
        self.labels.append(str(value))
        return UIElement()

    def page_title(self, title):
        self.page_titles.append(title)

    def colors(self, **_kwargs):
        return None

    def add_head_html(self, *_args, **_kwargs):
        return None

    def dark_mode(self, value):
        return UIElement(value=value)

    def run(self, *_args, **_kwargs):
        self.started = True

    def __getattr__(self, attr):
        if attr in {'element', 'button', 'icon', 'html', 'image', 'card', 'link', 'upload',
                    'textarea', 'timer', 'select', 'pagination', 'dialog', 'row'}:
            return lambda *_args, **_kwargs: UIElement()
        raise AttributeError(attr)


def test_main_registers_all_eight_pages_and_each_renders_for_both_languages(monkeypatch):
    fake_ui = FakeUI()
    mounts = []
    fake_nicegui = ModuleType('nicegui')
    fake_nicegui.app = SimpleNamespace(add_static_files=lambda *args: mounts.append(args))
    fake_nicegui.ui = fake_ui
    fake_nicegui.events = SimpleNamespace(UploadEventArguments=object)
    fake_nicegui.run = SimpleNamespace(io_bound=None)
    monkeypatch.setitem(sys.modules, 'nicegui', fake_nicegui)

    # Import only after installing the boundary double.
    module = importlib.import_module('main')
    module.main()

    assert fake_ui.started
    assert {mount[0] for mount in mounts} == {'/assets', '/styles', '/scripts'}
    assert set(fake_ui.routes) == {
        '/', '/about', '/eeg', '/ball-valve', '/convex-deepstack', '/flowdesk', '/partfinder', '/procurematch'
    }

    for page in fake_ui.routes.values():
        for language in ('EN', 'FR'):
            request = SimpleNamespace(cookies={'portfolio_theme': 'dark'})
            page(request, lang=language)

    # Every page generated a title and the solution routes communicate their true status.
    assert len(fake_ui.page_titles) == 16
    assert 'Coming soon' in fake_ui.labels
    assert 'Bientôt disponible' in fake_ui.labels
    assert '0.872' in fake_ui.labels
    assert '14.03×' in fake_ui.labels
