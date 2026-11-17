import hashlib
from io import BytesIO
import zipfile

import pytest

from scripts import prepare_render


@pytest.mark.parametrize('download', [b'catalog', b'corrupt', b'catalog-too-large'])
def test_download_publishes_only_the_committed_bytes(tmp_path, monkeypatch, download):
    expected = b'catalog'
    pointer = (f'version https://git-lfs.github.com/spec/v1\n'
               f'oid sha256:{hashlib.sha256(expected).hexdigest()}\nsize {len(expected)}\n').encode()
    relative = prepare_render.ARTIFACTS[0]
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_bytes(pointer)
    monkeypatch.setattr(prepare_render, 'ROOT', tmp_path)
    monkeypatch.setattr(prepare_render.subprocess, 'check_output', lambda *args, **kwargs: pointer)
    monkeypatch.setattr(prepare_render.urllib.request, 'urlopen', lambda *args, **kwargs: BytesIO(download))

    if download == expected:
        prepare_render.materialize(relative, 'a' * 40)
        assert target.read_bytes() == expected
    else:
        with pytest.raises(ValueError):
            prepare_render.materialize(relative, 'a' * 40)
        assert target.read_bytes() == pointer
    assert list(target.parent.iterdir()) == [target]


@pytest.mark.parametrize('name', ['../escape.png', '/escape.png', 'folder\\escape.png', 'script.html'])
def test_archive_rejects_unsafe_paths_before_writing(tmp_path, name):
    archive_path = tmp_path / 'images.zip'
    with zipfile.ZipFile(archive_path, 'w') as archive:
        archive.writestr('safe.png', b'preview')
        archive.writestr(name, b'bad')
    destination = tmp_path / 'images'
    with pytest.raises(ValueError):
        prepare_render.extract_images(archive_path, destination)
    assert not destination.exists()


def test_archive_preserves_preview_paths(tmp_path):
    archive_path = tmp_path / 'images.zip'
    with zipfile.ZipFile(archive_path, 'w') as archive:
        archive.writestr('.gitkeep', b'')
        archive.writestr('mcb_b/train/gear/part.png', b'preview')
    destination = tmp_path / 'images'
    prepare_render.extract_images(archive_path, destination)
    assert (destination / 'mcb_b/train/gear/part.png').read_bytes() == b'preview'
    assert not (destination / '.gitkeep').exists()
