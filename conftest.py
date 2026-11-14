import pytest
from pathlib import Path


def pytest_ignore_collect(collection_path, config):
    # Ignore imported environment trees before pytest stats invalid Linux symlinks.
    if collection_path.parent == Path(__file__).parent and (
        collection_path.name in {'lib64', 'lib', 'bin', 'include'} or
        collection_path.name.startswith('.venv')
    ):
        return True
    return None


def pytest_addoption(parser):
    parser.addoption('--run-browser', action='store_true', default=False,
                     help='Run the critical homepage browser workflows.')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--run-browser'):
        skip = pytest.mark.skip(reason='Browser workflows run separately with --run-browser.')
        for item in items:
            if item.get_closest_marker('browser'):
                item.add_marker(skip)
