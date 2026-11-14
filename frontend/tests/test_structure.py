"""Protect meaningful module boundaries and route inventory."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROUTES = {
    'home.py': '/',
    'about.py': '/about',
    'eeg.py': '/eeg',
    'ball_valve.py': '/ball-valve',
    'convex_deepstack.py': '/convex-deepstack',
    'flowdesk.py': '/flowdesk',
    'partfinder.py': '/partfinder',
    'procurematch.py': '/procurematch',
}


def test_each_page_declares_its_own_route():
    page_modules = {p.name for p in (ROOT / 'pages').glob('*.py') if p.name != '__init__.py'}
    assert page_modules == set(EXPECTED_ROUTES)
    for filename, url in EXPECTED_ROUTES.items():
        module = ast.parse((ROOT / 'pages' / filename).read_text(encoding='utf-8'))
        paths = [
            decorator.args[0].value
            for function in module.body
            if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef))
            for decorator in function.decorator_list
            if isinstance(decorator, ast.Call)
            and isinstance(decorator.func, ast.Attribute)
            and decorator.func.attr == 'page'
        ]
        assert paths == [url]


def test_composition_root_does_not_render_pages_or_define_css():
    module = ast.parse((ROOT / 'main.py').read_text(encoding='utf-8'))
    functions = {n.name for n in module.body if isinstance(n, ast.FunctionDef)}
    assert functions == {'main'}
    assert not any(isinstance(n, ast.ClassDef) for n in module.body)
    assert 'ui.run(' in (ROOT / 'main.py').read_text(encoding='utf-8')


def test_all_styles_are_external_files_and_mounted():
    styles = ROOT / 'styles'
    for filename in ('base.css', 'showcase.css', 'solutions.css', 'details.css', 'partfinder.css'):
        assert (styles / filename).is_file()
    layout = (ROOT / 'components/layout.py').read_text(encoding='utf-8')
    assert '/styles/' in layout
    sources = (file for file in ROOT.rglob('*.py') if 'tests' not in file.parts)
    assert not any(
        'ui.add_css(' in source or '.style(' in source
        for source in (file.read_text(encoding='utf-8') for file in sources)
    )


def test_expected_optional_art_assets_have_fallbacks():
    for filename in ('home.py', 'eeg.py', 'ball_valve.py', 'convex_deepstack.py'):
        text = (ROOT / 'pages' / filename).read_text(encoding='utf-8')
        assert '.is_file()' in text
