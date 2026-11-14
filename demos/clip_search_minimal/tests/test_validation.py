from io import BytesIO

import numpy as np
from PIL import Image
import pytest

from search_engine.validation import MAX_IMAGE_BYTES, InputError, read_reference_image, validate_description
from search_engine.runtime import SearchRuntime, SearchSession
from search_engine import runtime as runtime_module
from search_engine.errors import visitor_error


@pytest.mark.parametrize('text', ['x' * 2001, '\ud800', 'part\x00description'])
def test_invalid_description_is_rejected_before_embedding(tmp_path, monkeypatch, text):
    runtime = SearchRuntime(tmp_path / 'unused.db')
    runtime.ready = True
    monkeypatch.setattr(runtime_module, 'embed_query', lambda *args: pytest.fail('Must reject before inference'))
    with pytest.raises(InputError):
        SearchSession(runtime).submit(text, None)


def test_description_boundary_preserves_unicode_and_punctuation():
    assert validate_description(' pièce – écrou\n' ) == 'pièce – écrou'
    assert len(validate_description('é' * 2000)) == 2000


@pytest.mark.parametrize('format', ['PNG', 'JPEG', 'WEBP'])
def test_advertised_images_are_accepted(format):
    data = BytesIO()
    Image.new('RGB', (16, 8), 'red').save(data, format=format)
    with read_reference_image(data.getvalue()) as image:
        assert image.size == (16, 8) and image.mode == 'RGB'


def test_unadvertised_tiff_and_oversized_bytes_are_rejected():
    data = BytesIO()
    Image.new('RGB', (16, 16), 'red').save(data, format='TIFF')
    with pytest.raises(InputError):
        read_reference_image(data.getvalue())
    with pytest.raises(InputError, match='12 MB'):
        read_reference_image(b'x' * (MAX_IMAGE_BYTES + 1))


def test_image_dimensions_are_checked_before_pixel_decode():
    data = BytesIO()
    Image.new('1', (7000, 6000)).save(data, format='PNG')
    with pytest.raises(InputError, match='40 megapixels'):
        read_reference_image(data.getvalue())


def test_browser_error_never_contains_raw_exception_or_paths(caplog):
    secret = r'C:\private\customer.db: secret upstream content'
    message = visitor_error(RuntimeError(secret), 'search')
    assert secret not in message and secret not in caplog.text
    assert 'Reference:' in message
    assert 'RuntimeError' in caplog.text
