"""The model-output contract shared by catalog construction and live queries."""
import numpy as np

EMBEDDING_DIMENSION = 512
UNIT_NORM_TOLERANCE = 1e-4


def validate_embeddings(vectors: np.ndarray, rows: int) -> np.ndarray:
    values = np.asarray(vectors)
    if (values.shape != (rows, EMBEDDING_DIMENSION) or
            not np.issubdtype(values.dtype, np.floating) or not np.isfinite(values).all()):
        raise ValueError('Invalid CLIP embedding batch shape or numeric values.')
    norms = np.linalg.norm(values.astype(np.float64), axis=1)
    if not np.all(np.isclose(norms, 1, atol=UNIT_NORM_TOLERANCE, rtol=0)):
        raise ValueError('Invalid CLIP embedding normalization.')
    return values.astype('<f4', copy=False)
