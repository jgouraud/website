"""Launch the current portfolio from the repository root."""

from pathlib import Path
import runpy
import sys


if __name__ in {'__main__', '__mp_main__'}:
    frontend = Path(__file__).resolve().parent / 'frontend'
    sys.path.insert(0, str(frontend))
    runpy.run_path(str(frontend / 'main.py'), run_name=__name__)
