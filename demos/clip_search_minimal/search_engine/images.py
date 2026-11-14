"""Resolve image previews only from the explicitly configured public image root."""
from pathlib import Path
from urllib.parse import quote

from search_engine.settings import IMAGE_ROOT


def preview_url(db_image_path: str) -> str | None:
    if not db_image_path:
        return None
    value = db_image_path.replace('\\', '/')
    candidates = []
    # Original database paths may include a machine-specific absolute prefix.
    if 'output_data/images/' in value:
        candidates.append(IMAGE_ROOT / value.split('output_data/images/', 1)[1])
    if value.startswith('images/'):
        candidates.append(IMAGE_ROOT / value.removeprefix('images/'))
    candidates.append(IMAGE_ROOT / value)
    candidates.append(Path(value))
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.is_file() and resolved.is_relative_to(IMAGE_ROOT):
            return '/catalog-images/' + quote(resolved.relative_to(IMAGE_ROOT).as_posix(), safe='/')
    return None
