"""Compatibility hook for hosting the PartFinder backend in a NiceGUI app."""
from nicegui import app

from backend import register_backend

register_backend(app)


if __name__ in {'__main__', '__mp_main__'}:
    raise SystemExit('Run the portfolio frontend (main.py); PartFinder is available at /partfinder.')
