"""PartFinder's shared, read-only backend lifecycle for its host application."""

from __future__ import annotations

from typing import Any

from search_engine.http_limits import PublicCatalogImages, UploadLimitsMiddleware
from search_engine.runtime import SearchRuntime
from search_engine.settings import DATABASE, IMAGE_ROOT


runtime = SearchRuntime(DATABASE)
_registered = False


async def prepare_search() -> None:
    """Load CLIP and the catalog once when the host website starts."""
    from nicegui import run

    try:
        await run.io_bound(runtime.initialize)
        print(f'PartFinder ready: CLIP and {runtime.collection.size} catalog items cached.', flush=True)
    except Exception:
        print(f'PartFinder startup failed: {runtime.error}', flush=True)


def register_backend(app: Any) -> None:
    """Attach the demo backend's routes, limits, and startup work to a host app."""
    global _registered
    if _registered:
        return
    # The frontend's structural boundary double intentionally has no ASGI hooks.
    if not hasattr(app, 'on_startup'):
        return
    _registered = True
    app.add_middleware(UploadLimitsMiddleware)
    if IMAGE_ROOT.is_dir():
        app.mount('/catalog-images', PublicCatalogImages(directory=str(IMAGE_ROOT)), name='catalog-images')
    app.on_startup(prepare_search)
