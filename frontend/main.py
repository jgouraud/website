"""Composition root for the NiceGUI portfolio frontend.

All route views, copy, and CSS are owned by separate modules/files.
Run from this directory: python main.py
"""

from nicegui import app, ui

from app_config import ASSET_DIR, SCRIPTS_DIR, STYLES_DIR


def main() -> None:
    """Mount static resources, register independent pages, and start the server."""
    app.add_static_files('/assets', str(ASSET_DIR))
    app.add_static_files('/styles', str(STYLES_DIR))
    app.add_static_files('/scripts', str(SCRIPTS_DIR))

    # NiceGUI's page decorators register routes when their modules are imported.
    from pages import about, ball_valve, convex_deepstack, eeg, flowdesk, home, partfinder, procurematch  # noqa: F401
    partfinder.register_backend(app)

    favicon = ASSET_DIR / 'favicon.svg'
    ui.run(
        title='Julien Gouraud | Portfolio',
        favicon=favicon if favicon.is_file() else None,
        port=8080,
        reload=False,
    )


if __name__ in {'__main__', '__mp_main__'}:
    main()
