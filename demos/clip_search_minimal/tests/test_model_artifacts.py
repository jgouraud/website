from contextlib import closing
import hashlib
from io import BytesIO
import socket

import pytest

from search_engine import model_download as downloader
from search_engine.model_artifacts import ModelSetupError, ModelSpec, verify_checkpoint


def spec(data: bytes) -> ModelSpec:
    return ModelSpec('test-model', 'test.pt', hashlib.sha256(data).hexdigest(), 'https://models.test/test.pt')


@pytest.mark.parametrize('option', ['timeout', 'deadline'])
@pytest.mark.parametrize('value', [0, -1, float('inf'), float('nan')])
def test_download_rejects_unbounded_configuration_before_creating_files(tmp_path, option, value):
    cache = tmp_path / 'models'
    with pytest.raises(ValueError, match='configuration'):
        downloader.run_download_model(cache, spec=spec(b'model'), **{option: value})
    assert not cache.exists()


def test_verified_download_uses_finite_timeout_and_atomic_replacement(tmp_path, monkeypatch):
    data = b'checkpoint bytes'
    target = tmp_path / 'test.pt'
    target.write_bytes(b'damaged cache')
    calls = []
    class Opener:
        def open(self, url, *, timeout):
            calls.append((url, timeout))
            return closing(BytesIO(data))
    monkeypatch.setattr(downloader.urllib.request, 'build_opener', lambda *args: Opener())
    assert downloader.run_download_model(tmp_path, spec=spec(data), timeout=2) == target
    assert target.read_bytes() == data and calls == [('https://models.test/test.pt', 2)]
    verify_checkpoint(target, spec(data))
    assert not list(tmp_path.glob('.checkpoint-*'))


def test_bad_download_preserves_existing_checkpoint(tmp_path, monkeypatch):
    target = tmp_path / 'test.pt'
    target.write_bytes(b'previous cache')
    class Opener:
        def open(self, *args, **kwargs):
            return closing(BytesIO(b'wrong bytes'))
    monkeypatch.setattr(downloader.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(ModelSetupError, match='SHA-256'):
        downloader.run_download_model(tmp_path, spec=spec(b'expected bytes'))
    assert target.read_bytes() == b'previous cache'
    assert not list(tmp_path.glob('.checkpoint-*'))


def test_network_timeout_is_bounded_and_does_not_publish(tmp_path, monkeypatch):
    class Opener:
        def open(self, *args, **kwargs):
            raise socket.timeout('private upstream failure')
    monkeypatch.setattr(downloader.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(ModelSetupError, match='timed out') as error:
        downloader.run_download_model(tmp_path, spec=spec(b'model'))
    assert 'private upstream' not in str(error.value)
    assert not (tmp_path / 'test.pt').exists()


def test_download_deadline_discards_a_partial_checkpoint(tmp_path, monkeypatch):
    class Opener:
        def open(self, *args, **kwargs):
            return closing(BytesIO(b'model'))
    clock = iter([0, .1, 2])
    monkeypatch.setattr(downloader.time, 'monotonic', lambda: next(clock))
    monkeypatch.setattr(downloader.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(ModelSetupError, match='deadline'):
        downloader.run_download_model(tmp_path, spec=spec(b'model'), deadline=1)
    assert not (tmp_path / 'test.pt').exists()
    assert not list(tmp_path.glob('.checkpoint-*'))


def test_download_size_limit_stops_publication(tmp_path, monkeypatch):
    class Opener:
        def open(self, *args, **kwargs):
            return closing(BytesIO(b'model'))
    monkeypatch.setattr(downloader, 'MAX_CHECKPOINT_BYTES', 3)
    monkeypatch.setattr(downloader.urllib.request, 'build_opener', lambda *args: Opener())
    with pytest.raises(ModelSetupError, match='size limit'):
        downloader.run_download_model(tmp_path, spec=spec(b'model'))
    assert not (tmp_path / 'test.pt').exists()
