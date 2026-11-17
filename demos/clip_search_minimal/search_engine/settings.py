"""Only local read-only data paths and CLIP model settings."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Keep full local catalogs; clean deployments use the committed random sample.
DEFAULT_DATABASE = ROOT / 'data' / 'catalog.db'
if not DEFAULT_DATABASE.is_file():
    DEFAULT_DATABASE = ROOT / 'data' / 'deployment' / 'catalog.db'
DATABASE = Path(os.environ.get('CLIP_SEARCH_DB', str(DEFAULT_DATABASE))).expanduser()
IMAGE_ROOT = Path(os.environ.get('CLIP_SEARCH_IMAGES', str(ROOT / 'data' / 'images'))).expanduser().resolve()
MODEL_DIR = Path(os.environ.get('CLIP_MODEL_DIR', str(ROOT / 'models'))).expanduser().resolve()
MODEL_NAME = os.environ.get('CLIP_MODEL_NAME', 'ViT-B/32')
HOST = os.environ.get('CLIP_SEARCH_HOST', '127.0.0.1')
PORT = int(os.environ.get('CLIP_SEARCH_PORT', '8080'))
