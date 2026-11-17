"""Build the reproducible 1,000-item deployment sample without changing local data."""

from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1] / 'demos/clip_search_minimal/data'
SAMPLE_SIZE = 1000
SEED = 42


def main() -> None:
    source = ROOT / 'catalog.db'
    destination = ROOT / 'deployment'
    destination.mkdir(exist_ok=True)
    with source.open('rb') as stream:
        source_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
    with tempfile.TemporaryDirectory(dir=destination) as temporary:
        staging = Path(temporary)
        with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)) as original:
            rowids = [row[0] for row in original.execute(
                'SELECT rowid FROM items ORDER BY source_split, classification, id')]
            selected = random.Random(SEED).sample(rowids, SAMPLE_SIZE)
            with closing(sqlite3.connect(staging / 'catalog.db')) as sample:
                original.backup(sample)
                placeholders = ','.join('?' for _ in selected)
                sample.execute(f'DELETE FROM items WHERE rowid NOT IN ({placeholders})', selected)
                rows = sample.execute('SELECT image_path, source_split FROM items ORDER BY image_path').fetchall()
                metadata = {
                    'item_count': str(SAMPLE_SIZE), 'build_mode': 'random_sample',
                    'sample_seed': str(SEED), 'source_catalog_sha256': source_hash,
                    'split_counts': json.dumps(dict(Counter(row[1] for row in rows))),
                    'source_splits': json.dumps(sorted({row[1] for row in rows})),
                }
                sample.executemany('INSERT OR REPLACE INTO catalog_metadata VALUES (?, ?)', metadata.items())
                sample.commit()
                sample.execute('VACUUM')
                if sample.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                    raise ValueError('Sample catalog failed integrity validation')
        image_root = (ROOT / 'images').resolve()
        with zipfile.ZipFile(staging / 'images.zip', 'w', compression=zipfile.ZIP_STORED) as archive:
            for relative in sorted({row[0] for row in rows}):
                image = (image_root / relative).resolve()
                if not image.is_relative_to(image_root) or image.suffix.lower() != '.png':
                    raise ValueError(f'Invalid catalog preview path: {relative}')
                archive.write(image, relative)
        for name in ('catalog.db', 'images.zip'):
            (staging / name).replace(destination / name)
    print(f'Created {SAMPLE_SIZE} random catalog items with seed {SEED}; full local catalog unchanged.')


if __name__ == '__main__':
    main()
