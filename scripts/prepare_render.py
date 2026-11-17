"""Materialize the committed LFS artifacts before starting the website."""

import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import time
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEMO = Path('demos/clip_search_minimal')
ARTIFACTS = (DEMO / 'data/deployment/catalog.db', DEMO / 'models/ViT-B-32.pt',
             DEMO / 'data/deployment/images.zip')


def materialize(relative: Path, commit: str) -> None:
    """Use the committed LFS pointer as the size and SHA-256 authority."""
    pointer = subprocess.check_output(['git', 'show', f'{commit}:{relative.as_posix()}'], cwd=ROOT)
    match = re.fullmatch(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize ([0-9]+)\n', pointer)
    if not match:
        raise ValueError(f'{relative} must be committed with Git LFS')
    digest, size = match[1].decode(), int(match[2])
    if not 0 < size <= 1024 ** 3:
        raise ValueError(f'Unexpected artifact size: {relative}')
    target = ROOT / relative
    if target.is_file() and target.stat().st_size == size:
        with target.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() == digest:
                return
    url = f'https://media.githubusercontent.com/media/jgouraud/website/{commit}/{relative.as_posix()}'
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    started = time.monotonic()
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
            temporary = Path(output.name)
            actual, total = hashlib.sha256(), 0
            with urllib.request.urlopen(url, timeout=30) as response:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > size or time.monotonic() - started > 600:
                        raise ValueError(f'Artifact download exceeded its size or time limit: {relative}')
                    actual.update(chunk)
                    output.write(chunk)
            if total != size or actual.hexdigest() != digest:
                raise ValueError(f'Artifact checksum mismatch: {relative}')
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def extract_images(archive_path: Path, destination: Path) -> None:
    """Extract bounded PNG previews; reject paths that could escape the image root."""
    with zipfile.ZipFile(archive_path) as archive:
        entries = [entry for entry in archive.infolist() if entry.filename != '.gitkeep']
        if len(entries) > 20000 or sum(entry.file_size for entry in entries) > 1024 ** 3:
            raise ValueError('Preview archive exceeds deployment limits')
        for entry in entries:
            path = PurePosixPath(entry.filename)
            target = destination.joinpath(*path.parts).resolve()
            if (path.is_absolute() or '..' in path.parts or '\\' in entry.filename
                    or path.suffix.lower() != '.png'
                    or not target.is_relative_to(destination.resolve())):
                raise ValueError(f'Invalid preview path: {entry.filename}')
        # Validate every path before writing any preview. ZipFile also checks CRCs.
        archive.extractall(destination, members=entries)


def main() -> None:
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for relative in ARTIFACTS:
        print(f'Verifying {relative}', flush=True)
        materialize(relative, commit)
    extract_images(ROOT / DEMO / 'data/deployment/images.zip', ROOT / DEMO / 'data/images')
    print('PartFinder catalog, model, and preview images are ready.', flush=True)


if __name__ == '__main__':
    main()
