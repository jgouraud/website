"""Read-only adapters for the sample catalog and the original SQLite schema."""
from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

import numpy as np
from search_engine.embeddings import EMBEDDING_DIMENSION

@dataclass
class Collection:
    ids: list[str]
    names: list[str]
    image_paths: list[str]
    vectors: dict[str, np.ndarray]
    owners: dict[str, np.ndarray]
    classifications: list[str] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.ids)


def _normalized(blob: bytes | None) -> np.ndarray | None:
    if not isinstance(blob, (bytes, bytearray, memoryview)) or len(blob) != EMBEDDING_DIMENSION * 4:
        return None
    vector = np.frombuffer(blob, dtype='<f4')
    if not np.isfinite(vector).all():
        return None
    norm = np.linalg.norm(vector.astype(np.float64))
    return (vector.astype(np.float64) / norm).astype(np.float32) if np.isfinite(norm) and norm > 0 else None


def _load_catalog(connection: sqlite3.Connection) -> Collection:
    from search_engine.settings import MODEL_NAME

    metadata = dict(connection.execute('SELECT key, value FROM catalog_metadata'))
    if metadata.get('schema_version', '1') not in {'1', '2', '3', '4'}:
        raise ValueError('Unsupported catalog schema version. Rebuild with this application version.')
    if metadata.get('embedding_model') != MODEL_NAME:
        raise ValueError(f"Catalog uses {metadata.get('embedding_model')}; select that same CLIP model for queries.")
    # Load only searchable image vectors and display metadata, including for older catalogs.
    rows = connection.execute('''SELECT id, name, image_path, classification,
                                image_embedding
                                FROM items ORDER BY classification, id, source_split''').fetchall()
    vectors, owners = [], []
    for index, row in enumerate(rows):
        vector = _normalized(row['image_embedding'])
        if vector is not None:
            vectors.append(vector)
            owners.append(index)
    return Collection(
        [str(row['id']) for row in rows], [row['name'] for row in rows],
        [row['image_path'] for row in rows],
        {'image': np.vstack(vectors).astype(np.float32) if vectors else np.empty((0, EMBEDDING_DIMENSION), np.float32)},
        {'image': np.asarray(owners, dtype=np.int32)},
        [row['classification'] for row in rows],
    )


def load_collection(db_path: Path) -> Collection:
    """Read, but never create, update, or migrate the source database.

    Compatible with the existing Images and ImageViews schema. Stored
    descriptions, text embeddings, and legacy grayscale embeddings are ignored.
    """
    db_path = Path(db_path).expanduser().resolve()
    if not db_path.is_file():
        raise FileNotFoundError(f"Database not found: {db_path}. See README.md for setup.")

    # mode=ro prevents accidental CREATE or write operations.
    uri = f"file:{quote(db_path.as_posix(), safe='/:')}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA query_only = ON')
        tables = {
            row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')")
        }
        if 'items' in tables and 'catalog_metadata' in tables:
            return _load_catalog(connection)
        if 'Images' not in tables:
            raise ValueError("Expected an 'Images' table (see the database schema in README.md).")
        columns = {r[1] for r in connection.execute('PRAGMA table_info("Images")')}
        if 'Trial' not in columns:
            raise ValueError("The 'Images' table requires the existing 'Trial' primary-key column.")
        selected_columns = ['Trial', *[name for name in ('file_path', 'name', 'classification') if name in columns]]
        rows = connection.execute('SELECT ' + ', '.join(f'"{name}"' for name in selected_columns) + ' FROM Images').fetchall()
        ids = [str(row['Trial']) for row in rows]
        owner_indices = {item_id: index for index, item_id in enumerate(ids)}

        # The UI only shows a generic item title / image; not CRM metadata.
        names, image_paths = [], []
        for row in rows:
            image_path = str(row['file_path'] or '') if 'file_path' in columns else ''
            name = str(row['name'] or '').strip() if 'name' in columns else ''
            if not name:
                name = Path(image_path.replace('\\', '/')).stem or f'Item {row["Trial"]}'
            names.append(name)
            image_paths.append(image_path)

        vectors, owners = [], []

        # If a catalog row has no base image, use its first view for the thumbnail.
        if 'ImageViews' in tables:
            view_columns = {r[1] for r in connection.execute('PRAGMA table_info("ImageViews")')}
            if {'image_id', 'image_embedding'}.issubset(view_columns):
                for row in connection.execute('SELECT image_id, image_embedding FROM ImageViews'):
                    owner = owner_indices.get(str(row[0]))
                    vector = _normalized(row[1]) if owner is not None else None
                    if vector is not None:
                        vectors.append(vector)
                        owners.append(owner)
            if {'image_id', 'file_path'}.issubset(view_columns):
                for row in connection.execute('SELECT image_id, file_path FROM ImageViews'):
                    owner = owner_indices.get(str(row[0]))
                    if owner is not None and not image_paths[owner]:
                        image_paths[owner] = str(row[1] or '')

    classifications = [str(row['classification'] or '') if 'classification' in columns else '' for row in rows]
    return Collection(ids, names, image_paths,
                      {'image': np.vstack(vectors).astype(np.float32) if vectors else np.empty((0, EMBEDDING_DIMENSION), np.float32)},
                      {'image': np.asarray(owners, dtype=np.int32)}, classifications)
