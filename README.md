# Julien Gouraud — NiceGUI homepage prototype

This folder recreates the supplied light-blue homepage mockup with NiceGUI.

## Run

On Windows PowerShell, select the native environment for this terminal session:

```powershell
$env:UV_PROJECT_ENVIRONMENT = "$PWD\.venv-windows"
uv sync --locked
uv run --locked frontend/main.py
```

Using `.venv-windows` avoids trying to repair a Linux `.venv` copied into this
folder. Do not copy virtual environments between operating systems. The `uv`
commands below work in the same PowerShell session with this setting.

On Linux/macOS, from a clean checkout:

```bash
uv sync --locked
uv run --locked frontend/main.py
```

Then open **http://localhost:8080**.

`uv run --locked main.py` from the repository root starts the same frontend.
Restart the server after pulling changes; automatic reload is disabled.

The root uv environment includes the dependencies for PartFinder, using CPU
builds of PyTorch and torchvision on Linux and Windows. It is part of this site
at `/partfinder`; its existing catalog and checkpoint load once at website
startup, and neither startup nor inference downloads or builds assets.

Run backend tests from the project root:

```bash
uv run --locked --group test python -m pytest -q
```

Run the critical browser workflows separately:

```bash
uv run --locked --group browser playwright install --with-deps chromium
uv run --locked --group test --group browser python -m pytest -q tests/browser --run-browser
```

On Windows, browser tests use installed Chrome when available, or a Playwright
Chromium installation. CI runs backend checks on Windows/Linux
and the browser checks on Linux. See [engineering decisions](docs/engineering-decisions.md)
for stage contracts, failure guarantees, resource limits, and artifact migration.

## Render deployment

Use the repository root with build command
`pip install -r requirements.txt && python scripts/prepare_render.py`
and start command `python main.py`. The `.python-version` file selects Python
3.12; remove any conflicting `PYTHON_VERSION` override in Render's environment
settings. The server binds to `0.0.0.0` and Render's `PORT` (8080 locally).

`requirements.txt` is exported from the existing lockfile, including CPU-only
PyTorch on Linux and Windows. After changing dependencies, regenerate it with:

```bash
uv export --locked --no-dev --no-hashes --no-emit-project --no-annotate --emit-index-url --format requirements-txt --output-file requirements.txt
```

The 1,000-item catalog sample, CLIP checkpoint, and matching preview archive are versioned with Git
LFS. The build step materializes these files from this public GitHub repository
at the deployed commit, verifies their LFS SHA-256 checksums and sizes, and
extracts the previews. It also works when the checkout contains only LFS pointers;
Render does not need a Git LFS client. A failed download or checksum fails the
build. Model loading and search never download or rebuild artifacts.

Keep `CLIP_SEARCH_DB`, `CLIP_SEARCH_IMAGES`, and `CLIP_MODEL_DIR` unset to use
the bundled artifacts. Existing environment overrides must point to valid files.
For a local clone, install Git LFS and run `git lfs pull`, then run
`python scripts/prepare_render.py` once. The sample and previews live under
`demos/clip_search_minimal/data/deployment/`. Recreate both from the full local
catalog with `python scripts/sample_catalog.py` (uniform sampling without
replacement, seed 42). The sample records the source catalog checksum and seed.
The full local catalog and extracted previews stay out of Git. An existing local
`data/catalog.db` takes precedence; clean deployments use the sample.

Use an instance with sufficient memory for CPU CLIP inference. The 512 MB free
instance is insufficient for the current model, even with this smaller catalog.
Confirm both the homepage and a successful search after deployment;
an HTTP response alone does not establish search readiness. LFS storage and
downloads use the repository owner's GitHub LFS allowance.

## Important

- The sun/moon button beside the language selector switches between light mode and a dark blue theme. Light mode is the default; the selected theme is remembered in this browser across language changes, reloads, and return visits.
- Academic project cards fit their 25% smaller illustrations without the empty space left by visual scaling. Portrait tablets and phones use compact image-and-title rows. Navigation moves to a second row on tablets; small landscape phones use a single compact header row.
- Live demo cards use illustrations in `frontend/assets/`. Hover or focus reveals the story panels; click or tap a card or its arrow to open its demo. Keyboard users can focus a link and press Enter. Destinations are defined in `DEMO_ROUTES` in `frontend/content/site.py`, including PartFinder at `/partfinder`.
- **Navigation and most social buttons are placeholders.** The hero's LinkedIn button opens Julien Gouraud's LinkedIn profile in a new tab. The GitHub button still needs a destination. PartFinder is an integrated business-demo page with search, catalog browsing, and classification filtering.
- Below the hero, **Business Solutions - Live Demos** presents PartFinder, FlowDesk, and ProcureMatch. **Research Papers & Academic Projects** presents the three academic projects.
- The language switch is live. Select EN or FR to reload the page in that language; the selection is retained in the `?lang=EN` or `?lang=FR` URL. The copy for both languages is in the `COPY` dictionary.
- The hero uses `assets/portrait.png` and `assets/portrait-dark.png` for the two themes. Replace these to change the portrait; a placeholder is shown if the light portrait is missing. You can adjust `.hero-portrait` in the CSS string if necessary.
- All other non-NiceGUI visual assets are in `assets/`: three project illustrations extracted from the supplied mockup, a scalable wave background and a small Python logo SVG.
- The three project illustrations are **conceptual homepage art extracted from the mockup**, not scientific results or actual screenshots from project reports. Swap them for authentic figures later.
- The prototype uses NiceGUI widgets for buttons, icons, labels, images and cards, plus self-contained CSS for the appearance.
- It runs without external fonts, icon CDNs, or image services, after NiceGUI has been installed.

## Layout structure

`frontend/main.py` — portfolio composition root  
`assets/driving-planning.png` — first featured project artwork  
`assets/eeg-decoding.png` — second featured project artwork  
`assets/rocket-landing.png` — third featured project artwork  
`assets/hero-waves.svg` — light blue wireframe waves behind the hero  
`assets/PartFinder illustration.png` — PartFinder banner and full storytelling preview  
`assets/FlowDesk illustration.jpg` — FlowDesk banner and full storytelling preview  
`assets/ProcureMatch illustration.png` — ProcureMatch banner and full storytelling preview
