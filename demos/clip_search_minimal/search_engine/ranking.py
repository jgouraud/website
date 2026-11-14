"""CLIP ranking of query text and images against catalog image embeddings.

Each cosine similarity channel is reduced to the best crop per item and
min-max scaled before averaging all available channels. No database writes.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from search_engine.database import Collection, EMBEDDING_DIMENSION

SCORE_LABELS = {
    'global': 'Combined',
    'image': 'Image → image',
    'text_to_image': 'Text → image',
}


@dataclass(frozen=True)
class Result:
    item_id: str
    name: str
    image_path: str
    scores: dict[str, float]
    classification: str = ''


def _result(collection: Collection, index: int, scores: dict[str, float]) -> Result:
    return Result(collection.ids[index], collection.names[index], collection.image_paths[index], scores,
                  collection.classifications[index] if collection.classifications else '')


def browse(collection: Collection, classification: str | None = None, limit: int = 100) -> list[Result]:
    return [_result(collection, index, {}) for index in range(collection.size)
            if not classification or (collection.classifications and collection.classifications[index] == classification)][:limit]


def _unit(vector: np.ndarray | None) -> np.ndarray | None:
    if vector is None:
        return None
    vector = np.asarray(vector, dtype=np.float32).reshape(-1)
    if vector.shape != (EMBEDDING_DIMENSION,):
        raise ValueError(f'Query CLIP embedding must have {EMBEDDING_DIMENSION} dimensions.')
    if not np.isfinite(vector).all():
        raise ValueError('Query CLIP embeddings must contain only finite numbers.')
    norm = np.linalg.norm(vector.astype(np.float64))
    if not np.isfinite(norm):
        raise ValueError('Query CLIP embedding norm must be finite.')
    return (vector.astype(np.float64) / norm).astype(np.float32) if norm > 0 else None


def _best_scores(collection: Collection, query: np.ndarray | None) -> np.ndarray:
    best = np.full(collection.size, np.nan, dtype=np.float32)
    matrix = collection.vectors['image']
    if query is None or matrix.size == 0:
        return best
    raw = matrix @ query
    best[:] = -np.inf
    np.maximum.at(best, collection.owners['image'], raw)
    best[np.isneginf(best)] = np.nan
    return best


def _minmax(scores: np.ndarray) -> np.ndarray:
    valid = np.isfinite(scores)
    normalized = np.full_like(scores, np.nan)
    if not np.any(valid):
        return normalized
    minimum = scores[valid].min()
    maximum = scores[valid].max()
    normalized[valid] = 1.0 if np.isclose(minimum, maximum) else (scores[valid] - minimum) / (maximum - minimum)
    return normalized


def rank(
    collection: Collection,
    *,
    query_text: np.ndarray | None = None,
    query_image: np.ndarray | None = None,
    sort_by: str = 'global',
    limit: int = 24,
    classification: str | None = None,
) -> list[Result]:
    if query_text is None and query_image is None:
        raise ValueError('Enter text, upload an image, or use both.')
    if sort_by not in SCORE_LABELS:
        raise ValueError(f'Unknown scoring channel: {sort_by}')

    text = _unit(query_text)
    image = _unit(query_image)
    channels = {
        'image': _best_scores(collection, image),
        'text_to_image': _best_scores(collection, text),
    }
    if classification:
        eligible = np.asarray([value == classification for value in collection.classifications], dtype=bool)
        if eligible.size != collection.size:
            return []
        # Filter before normalization so excluded classes cannot affect scores.
        channels = {key: np.where(eligible, values, np.nan) for key, values in channels.items()}
    scaled = {key: _minmax(np.asarray(value, dtype=np.float32)) for key, value in channels.items()}
    # Avoid 'Mean of empty slice' warnings and preserve item-level missingness.
    stacked = np.vstack(list(scaled.values()))
    valid = np.isfinite(stacked)
    count = valid.sum(axis=0)
    combined = np.divide(np.nansum(stacked, axis=0), count, out=np.full(collection.size, np.nan), where=count > 0)
    scaled['global'] = combined

    sortable = scaled[sort_by]
    order = np.argsort(np.nan_to_num(sortable, nan=-np.inf), kind='stable')[::-1]
    selected = order[np.isfinite(sortable[order])][:max(0, limit)]
    return [
        _result(collection, int(i), {key: float(values[i]) for key, values in scaled.items()})
        for i in selected
    ]
