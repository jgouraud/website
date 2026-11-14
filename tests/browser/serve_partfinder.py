"""Test composition root for the integrated portfolio PartFinder route."""
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'demos/clip_search_minimal'))
sys.path.insert(0, str(ROOT / 'frontend'))

from search_engine import clip_model


def embed_query(text, image):
    vector = np.eye(1, 512, dtype=np.float32)[0]
    return (vector if text else None, vector if image else None)


clip_model.preload_model = lambda: None
clip_model.embed_query = embed_query

from nicegui import app, ui
from app_config import ASSET_DIR, SCRIPTS_DIR, STYLES_DIR
from pages import ball_valve, convex_deepstack, eeg, flowdesk, home, partfinder, procurematch  # noqa: F401

app.add_static_files('/assets', str(ASSET_DIR))
app.add_static_files('/styles', str(STYLES_DIR))
app.add_static_files('/scripts', str(SCRIPTS_DIR))
partfinder.register_backend(app)

ui.run(host='127.0.0.1', port=int(sys.argv[1]), show=False, reload=False)
