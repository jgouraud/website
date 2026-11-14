"""Trusted checkpoint identity; application/model loading never downloads files."""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
from pathlib import Path

from search_engine.settings import MODEL_DIR, MODEL_NAME


@dataclass(frozen=True)
class ModelSpec:
    name: str
    filename: str
    sha256: str
    url: str


# Identity from OpenAI CLIP's model registry at the revision pinned in uv.lock.
VIT_B_32 = ModelSpec(
    'ViT-B/32', 'ViT-B-32.pt',
    '40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af',
    'https://openaipublic.azureedge.net/clip/models/'
    '40d365715913c9da98579312b702a82c18be219cc2a73407c4526f58eba950af/ViT-B-32.pt',
)
MAX_CHECKPOINT_BYTES = 512 * 1024 * 1024
PREPROCESSING_REVISION = 'exif-rgb-thumbnail2048-white-square-lanczos224-clip-v2'


class ModelSetupError(RuntimeError):
    pass


def verify_checkpoint(path: Path, spec: ModelSpec = VIT_B_32) -> None:
    if not path.is_file() or not 0 < path.stat().st_size <= MAX_CHECKPOINT_BYTES:
        raise ModelSetupError('Model checkpoint is missing. Add the verified ViT-B-32.pt checkpoint before starting search.')
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    if digest != spec.sha256:
        raise ModelSetupError('Model checkpoint checksum is invalid. Replace it with the verified ViT-B-32.pt checkpoint.')


@lru_cache(maxsize=1)
def verified_checkpoint_path() -> Path:
    if MODEL_NAME != VIT_B_32.name:
        raise ModelSetupError('This catalog supports the verified ViT-B/32 checkpoint only.')
    path = MODEL_DIR / VIT_B_32.filename
    verify_checkpoint(path)
    return path


def model_provenance() -> dict[str, str]:
    verified_checkpoint_path()
    return {
        'embedding_model': VIT_B_32.name,
        'checkpoint_sha256': VIT_B_32.sha256,
        'preprocessing_revision': PREPROCESSING_REVISION,
    }
