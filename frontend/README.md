# Julien Gouraud — modular NiceGUI frontend

This is a modular NiceGUI portfolio with seven public routes, English/French copy,
dark-mode persistence, responsive styles, and an integrated PartFinder search demo.

## Run locally

Requires **Python 3.10+**. From the `frontend/` folder:

```bash
python -m pip install -r requirements.txt
python main.py
```

Open **http://localhost:8080**. Change the port in `main.py` if needed. Run the tests with `python -m pytest tests -q` (pytest must be installed).

## Project layout

```text
frontend/
├── main.py                 # Composition root only: static resources, route registration, server
├── app_config.py           # Paths, defaults, optional social links
├── utils.py                # Asset URL, language normalization, localized text
├── pages/                  # Exactly one Python module per public route
│   ├── home.py             # /
│   ├── eeg.py              # /eeg
│   ├── ball_valve.py       # /ball-valve
│   ├── convex_deepstack.py # /convex-deepstack
│   ├── flowdesk.py         # /flowdesk
│   ├── partfinder.py       # /partfinder
│   └── procurematch.py     # /procurematch
├── components/             # Shared header, cards, and business solution presentation
├── content/                # Localized copy and project metadata (no UI code)
├── styles/                 # base.css, showcase.css, solutions.css, details.css, partfinder.css
├── scripts/showcase.js     # Homepage pointer/keyboard showcase interaction
├── assets/                 # Small built-in SVG resources + optional original artwork
├── tests/                  # Behavior + architecture regression checks
├── requirements.txt
└── AGENTS.md               # Supplied coding standard, unchanged
```

Each `pages/*.py` file declares its own `@ui.page` route and renders the page. Shared components are intentionally thin. `main.py` owns only the static-resource mounts, imports that register the route modules, and server startup. CSS is never embedded in Python.

PartFinder's UI is part of this frontend. Its read-only catalog, model loading,
catalog-image route, and upload limits remain in `demos/clip_search_minimal` and
are registered when this website starts. The existing model and catalog load once
at startup; no catalog-building pipeline is included.

## Optional original artwork

The source application referenced a separate `assets/` directory, **which was not supplied**. This refactor includes the small SVG resources needed for the header, favicon, and controls. All missing media use the source application's fallbacks rather than broken images or invented study results. To restore the original visual appearance, copy the original files (when available) into `frontend/assets/`, preserving names:

- Home: `portrait.png`, optionally `portrait-dark.png`; `PartFinder illustration.png`, `FlowDesk illustration.jpg`, `ProcureMatch illustration.png`
- Academic previews: `driving-planning.svg`, `eeg-decoding.svg` (or `eeg-decoding.png` on the EEG detail), `rocket-landing.svg`, `ball-valve-anomaly.svg`
- Research: `banner_illustration.png`, `figure6_accuracy_cost_zoom.png`
- EEG: `roc_auc_model_comparison.svg`, `project_report.pdf`
- Ball-valve: `ball-valve-test-results.png`, `CIVIL426_Final_Project_Report.pdf`

**Note:** The source uses `project_report.pdf` for both the EEG and Convex DeepStack paper. If these are different PDFs, give them distinct filenames in `content/eeg.py` and `content/research.py` before adding the reports. The homepage's PartFinder and two academic previews have no dedicated destination in the supplied code, so they remain informational previews. The GitHub link is hidden until a real URL is set in `app_config.py`. The About menu item links to the portfolio introduction at the top of the homepage.

## Architecture decisions

- **Stack preserved:** NiceGUI + FastAPI; no frontend framework migration, backend rewrite, external API, database, or new personal-data collection.
- **Presentation separated:** page modules own composition, components own shared presentation, content modules own strings, and CSS/JS live in discrete static files.
- **Assets degrade safely:** optional graphics and PDF links render only when files exist; links to unpublished content do not appear as working downloads.
- **State unchanged:** language is encoded as a validated `?lang=EN|FR` query value; display theme persists through the source `portfolio_theme` cookie. There are no logins, form submissions, or persistent server-side user records.

## Known limits

Business solution pages intentionally say **Coming soon**, as in the source. Screenshots/visual fidelity cannot be matched exactly without the missing artwork. The UI remains functional with fallbacks. This package does not assert that the future business demos are implemented.

## Browser regression checks

The source-level and page-composition checks run without NiceGUI installed. To exercise real pages and interactions in a browser, install `pytest`, `playwright`, and its Chromium browser, start `python main.py` in a separate shell, then run:

```bash
RUN_E2E=1 python -m pytest tests/e2e -q
```

The browser tests cover language switching, dark mode, business-page status messaging, and return navigation. They are opt-in because they require a running web server and the external browser runtime. These checks have not been run in the supplied execution environment; package installation was unavailable there.
