"""Julien Gouraud — NiceGUI portfolio and business-solution preview pages.

Run alongside the original assets/ directory:
    pip install nicegui
    python main.py

Routes: /, /eeg, /ball-valve, /convex-deepstack, /flowdesk, /procurematch. Each supports ?lang=EN or ?lang=FR.
The two solution pages reuse the existing homepage illustrations directly,
clipped to their top 416 pixels (from the 1536 × 1024 source images).
"""

from pathlib import Path
from typing import Callable
from urllib.parse import quote
from fastapi import Request
from nicegui import app, ui

ROOT = Path(__file__).resolve().parent
ASSET_DIR = ROOT / 'assets'
DEFAULT_LANGUAGE = 'EN'
LINKEDIN_URL = 'https://www.linkedin.com/in/julien-gouraud-5783962b8'
GITHUB_URL = ''

# The original assets directory should be kept next to this script.
# Allow the Python module to load even when the assets were not included in a transfer.
ASSET_DIR.mkdir(parents=True, exist_ok=True)
app.add_static_files('/assets', str(ASSET_DIR))

COPY = {
    'EN': {
        'nav': ['Home','Business Solutions', 'Academic Projects', 'Research Papers', 'About'],
        'eyebrow': 'AI ENGINEER   •   WORKFLOW AUTOMATION   •   AGENTIC AI',
        'pitch': 'Automating the mundane to help teams focus on high-value tasks',
        'featured': 'Academic Projects',
        'research_heading': 'Research Papers',
        'research_project_title': 'Convex DeepStack: More Reliable Deep Learning',
        'show_all_academic': 'Show all academic projects',
        'explore': 'Business Solutions - Live Demos',
        'show_all': 'Show all',
        'show_all_business': 'Show all business solutions',
        'show_all_research': 'Show all research papers and academic projects',
        'clip_title': 'PartFinder',
        'clip_description': 'Find mechanical parts using an image or text',
        'clip_image_alt': 'PartFinder searches an inventory by photo or text, finds a matching plastic clip, and identifies its storage bin.',
        'flowdesk_title': 'FlowDesk',
        'flowdesk_description': 'Automate request routing and follow-up',
        'flowdesk_image_alt': 'FlowDesk request routing and follow-up workflow illustration.',
        'procurematch_title': 'ProcureMatch',
        'procurematch_description': 'Match invoices to purchase orders and flag discrepancies',
        'procurematch_image_alt': 'ProcureMatch compares financial documents and flags discrepancies using OCR.',
        'dark_theme': 'Switch to dark mode',
        'light_theme': 'Switch to light mode',
        'projects': [
            'Self Driving Car',
            'Seizures in EEGs',
            'Rocket Landing',
            'Ball Valve Anomaly Detection',
        ],
        'portrait_placeholder': 'Add assets/portrait.png',
    },
    'FR': {
        'nav': ['Accueil', 'Solutions professionnelles', 'Projets académiques', 'Articles de recherche', 'À propos'],
        'eyebrow': 'AUTOMATISATION   •   INGÉNIEUR IA   •   IA AGENTIQUE',
        'pitch': "Des systèmes d’IA concrets, des agents au déploiement.",
        'featured': 'Projets académiques',
        'research_heading': 'Articles de recherche',
        'research_project_title': 'Convex DeepStack : un deep learning plus fiable',
        'show_all_academic': 'Voir tous les projets académiques',
        'explore': 'Démos interactives & produits concrets',
        'show_all': 'Tout voir',
        'show_all_business': 'Voir toutes les solutions professionnelles',
        'show_all_research': 'Voir tous les articles de recherche et projets académiques',
        'clip_title': 'Moteur de recherche basé sur CLIP',
        'clip_description': 'Trouvez des pièces mécaniques avec une image, une description ou les deux.',
        'clip_image_alt': 'PartFinder recherche une pièce par photo ou texte, retrouve un clip en plastique et identifie son bac de stockage.',
        'flowdesk_title': 'FlowDesk',
        'flowdesk_description': 'Automatisez l’acheminement des demandes et leur suivi',
        'flowdesk_image_alt': 'Illustration du routage et du suivi des demandes avec FlowDesk.',
        'procurematch_title': 'ProcureMatch',
        'procurematch_description': 'Outil de signalement automatique des écarts financiers avec OCR',
        'procurematch_image_alt': 'ProcureMatch compare les documents financiers et signale les écarts avec OCR.',
        'dark_theme': 'Activer le mode sombre',
        'light_theme': 'Activer le mode clair',
        'projects': [
            'Planification de conduite autonome',
            'Détection épilépsie via EEG',
            'Atterrissage de fusée par MPC',
            'Anomalies des vannes hydrauliques',
        ],
        'portrait_placeholder': 'Ajouter assets/portrait.png',
    },
}

CSS = r'''
:root {
    --ink: #09163c;
    --muted: #2a395d;
    --blue: #0865ce;
    --line: #d6e3f9;
    --card: #f9fbff;
    --shadow: 0 7px 21px rgba(49, 86, 153, .065);
    --page-gutter: clamp(16px, 4vw, 56px);
    --content-width: 1600px;
    --section-gap: clamp(10px, 2.5svh, 28px);
    --hero-base-height: clamp(100px, 21svh, 200px);
    --hero-growth: calc(var(--hero-base-height) * .2);
    --hero-height: calc((var(--hero-base-height) + var(--hero-growth)) * .9);
    --project-preview-limit: clamp(72px, calc(100svh - 440px), 300px);
    --demo-preview-height: clamp(64px, 12svh, 104px);
}
* { box-sizing: border-box; }
html, body, #app { min-height: 100%; margin: 0; }
body {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    color: var(--ink);
    background:
      radial-gradient(ellipse 56% 34% at 86% 67%, #e5f0ff 0%, transparent 85%),
      linear-gradient(180deg, #f2f7ff 0%, #f6f9ff 58%, #f4f8ff 100%);
}
.nicegui-content { padding: 0 !important; gap: 0 !important; min-height: 100svh; }
/* Follow viewport changes immediately, without waiting for Quasar's resize update. */
.nicegui-layout, .nicegui-layout > .q-page-container > .q-page { min-height: 100svh !important; }
.q-btn { text-transform: none !important; }

/* NAVIGATION */
.site-header { width: 100%; position: relative; z-index: 3; }
.header-inner {
    width: min(var(--content-width), calc(100% - 2 * var(--page-gutter)));
    min-height: clamp(42px, 7svh, 56px);
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}
.brand { display: flex; align-items: center; flex: 0 0 auto; gap: 16px; }
.brand-mark { font-size: 34px !important; font-weight: 800 !important; letter-spacing: -3px; line-height: 1; color: #1067cb; }
.brand-divider { width: 1px; height: 30px; background: #91a6c8; }
.brand-name { font-size: 20px !important; font-weight: 750 !important; letter-spacing: -.65px; white-space: nowrap; }
.nav-links { display: flex; align-items: center; justify-content: center; gap: clamp(4px, 1vw, 16px) !important; flex-wrap: nowrap !important; min-width: 0; }
.nav-link.q-btn {
    min-height: 36px; min-width: 0; padding: 0 10px; border-radius: 11px;
    color: var(--ink); font-size: 15px; font-weight: 500;
    cursor: default;
}
.nav-link .q-btn__content { flex-wrap: nowrap; }
.nav-link .q-btn__content .block { min-width: 0; white-space: normal; line-height: 1.2; }
.nav-link:first-child, .nav-link:last-child { flex-shrink: 0; }
.nav-link .q-icon { font-size: 21px; margin-right: 6px; }
.nav-link.active.q-btn { color: white; background: #1067cb; }
.language-switch { display: flex; align-items: center; gap: 0 !important; flex: 0 0 auto; border: 1px solid #c5dbfb; border-radius: 40px; padding: 2px; }
.lang-button.q-btn { min-height: 30px; min-width: 44px; border-radius: 35px; font-size: 14px; padding: 0; color: #102754; cursor: default; }
.lang-button.selected.q-btn { color: white; background: #0d67c9; box-shadow: 0 3px 9px #9fc5ef; }
.header-controls { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.theme-toggle.q-btn {
    width: 38px; min-width: 38px; height: 38px; padding: 0;
    border: 1px solid #c5dbfb; border-radius: 50%; color: var(--ink);
    background: rgba(255,255,255,.55); cursor: pointer;
}
.theme-toggle:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }

/* HERO */
.hero-shell {
    position: relative;
    width: 100%;
    min-height: var(--hero-height);
    background: linear-gradient(120deg, #f6faff 10%, #edf5ff 70%, #e5f1ff 100%);
    isolation: isolate;
    overflow: hidden;
}
.hero-shell::before {
    content: ''; position: absolute; inset: 0; z-index: 0;
    background: url('/assets/hero-waves.svg') center bottom / 100% 100% no-repeat;
    pointer-events: none;
}
.hero-inner {
    z-index: 1; position: relative; display: grid;
    grid-template-columns: fit-content(min(750px, 67%)) minmax(0, 1fr);
    align-items: center; width: 100%; min-height: var(--hero-height);
    padding-left: max(var(--page-gutter), calc((100% - var(--content-width)) / 2));
}
.hero-copy { position: relative; z-index: 2; min-width: 0; padding: clamp(8px, 1.5svh, 16px) 0; }
.hero-eyebrow { color: #0866cc !important; font-size: clamp(12px, 1.2vw, 16px) !important; font-weight: 650 !important; letter-spacing: 1.2px; }
.hero-pitch { margin: 6px 0 0; color: #19274c !important; font-size: clamp(18px, 1.7vw, 24px) !important; font-weight: 400 !important; line-height: 1.35; letter-spacing: -.2px; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 10px !important; margin-top: clamp(6px, 1.2svh, 12px); }
.cta.q-btn { min-height: 42px; border-radius: 10px; font-size: 16px; font-weight: 500; padding: 0 18px; cursor: default; }
.cta .q-icon { font-size: 22px; }
.primary-cta.q-btn { color: white; background: #116bcf; box-shadow: none; }
.secondary-cta.q-btn { color: #10264d; border: 1.5px solid #0965d5; background: rgba(255,255,255,.73); }
.hero-portrait {
    position: absolute !important;
    /* Center within the remaining grid column, extending behind copy if narrow. */
    grid-column: 2; grid-row: 1;
    right: 0; bottom: 0;
    width: max(120px, 100%); height: 100%;
    object-fit: contain;
    z-index: 1;
    pointer-events: none;
}
.hero-portrait .q-img__image { object-fit: contain !important; object-position: center bottom !important; }
.portrait-placeholder {
    width: min(200px, 100%); min-width: 120px; height: 90%;
    position: absolute; grid-column: 2; grid-row: 1;
    left: 50%; bottom: 0; transform: translateX(-50%); z-index: 1;
    pointer-events: none;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border: 1.4px dashed rgba(69,126,210,.28); border-radius: 48% 48% 16px 16px;
    background: linear-gradient(140deg,rgba(219,236,255,.18),rgba(203,225,249,.27));
    color: #84abe2;
}
.placeholder-icon { font-size: 128px !important; opacity: .43; }
.placeholder-label { color:#7698bd; font-size:13px !important; opacity:.85; }

/* CONTENT */
.main-content {
    container-type: inline-size;
    --content-top-gap: clamp(4px, .8svh, 8px);
    --project-preview-height: min(var(--project-preview-limit), calc(((100cqw - 2 * clamp(10px, 1.5vw, 20px)) / 3 - 16px) * 9 / 16));
    --preview-height: calc((var(--project-preview-height) + var(--demo-preview-height) - var(--hero-growth)) / 2);
    width: min(var(--content-width), calc(100% - 2 * var(--page-gutter)));
    margin: 0 auto; padding: var(--content-top-gap) 0 var(--section-gap);
    flex: 1; display: flex; flex-direction: column; justify-content: flex-start;
    overflow-anchor: none;
}
.main-content > section { width: 100%; }
.section-title { margin: 0 0 clamp(4px, .8svh, 8px); font-size: clamp(15px, 2vw, 20px); letter-spacing: -.7px; line-height: 1.3; font-weight: 700; }
.section-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: clamp(4px, .8svh, 8px); }
.section-header .section-title { min-width: 0; margin-bottom: 0; }
.show-all { display: inline-flex; align-items: center; gap: 5px; flex-shrink: 0; color: #1067cb !important; font-size: clamp(12px, 1.2vw, 15px); font-weight: 600; white-space: nowrap; text-decoration: none !important; }
.show-all .q-icon { font-size: 18px; }
.show-all:hover { text-decoration: underline !important; }
.show-all:focus-visible { outline: 2px solid var(--blue); outline-offset: 4px; border-radius: 3px; }
.body--dark .show-all { color: var(--blue) !important; }
.projects-collapse { display: grid; grid-template-rows: 1fr; opacity: 1; transition: grid-template-rows .38s ease, opacity .25s ease; }
.projects-collapse-inner { min-height: 0; overflow: hidden; }
.main-content.demo-expanded .projects-collapse { grid-template-rows: 0fr; opacity: 0; pointer-events: none; }
.projects-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); align-items: start; gap: clamp(10px, 1.5vw, 20px); width: 100%; }
.project-card.q-card {
    border-radius: 13px;
    background: rgba(255,255,255,.57);
    border: 1px solid var(--line);
    padding: 5px;
    gap: 0 !important;
    min-width: 0;
    width: fit-content; max-width: 75%; justify-self: center;
    box-shadow: var(--shadow);
    overflow: hidden;
}
/* Size the layout itself to the smaller artwork, instead of scaling inside a large card. */
.project-image {
    display: block; width: auto; max-width: 100%; height: calc(var(--preview-height) * .75); aspect-ratio: auto;
    max-height: calc(var(--preview-height) * .75);
    flex-shrink: 0; border-radius: 10px; overflow: hidden;
    background: transparent; object-fit: contain;
    align-self: center; justify-self: center;
}
.project-bottom { contain: inline-size; display: flex; justify-content: space-between; align-items:center; width: 100%; gap: 6px !important; padding: 4px 0 0; min-height: 32px; min-width: 0; }
.project-card-clickable { position: relative; transition: border-color .2s ease, box-shadow .2s ease; }
.project-card-clickable:hover, .project-card-clickable:focus-within { border-color: var(--blue); box-shadow: 0 8px 24px rgba(12, 67, 139, .15); }
.project-card-overlay { position: absolute; inset: 0; z-index: 2; display: block; border-radius: inherit; text-decoration: none !important; }
.project-card-overlay:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }
.project-title { font-size: clamp(15px, 1.4vw, 19px) !important; font-weight: 700 !important; line-height: 1.2; letter-spacing: -.4px; color: var(--ink); }
.circle-arrow { display: flex; align-items:center; justify-content:center; width: 32px; height:32px; flex:0 0 auto; border-radius:50%; color:#004dbe; background:#e9f2ff; }
.circle-arrow .q-icon { font-size: 20px; }

.main-content > section + section { margin-top: max(var(--section-gap), calc(2 * var(--section-gap) - var(--content-top-gap))); }
.demos-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); align-items: start; gap: clamp(10px, 1.5vw, 20px); }
.demo-card.q-card {
    container-type: inline-size;
    display: block; min-width: 0; padding: 6px; border: 1px solid var(--line);
    border-radius: 17px; background: rgba(255,255,255,.57); box-shadow: var(--shadow);
    overflow: hidden;
    transition: border-color .2s ease, box-shadow .2s ease;
}
.demo-card.q-card:hover { border-color: var(--blue); box-shadow: 0 8px 24px rgba(12, 67, 139, .15); }
.demo-card:focus-visible { outline: 3px solid var(--blue); outline-offset: 4px; }
/* The story panels start below y=419 in all three 1536 x 1024 illustrations. */
.demo-banner {
    position: relative; width: 100%; height: calc(100cqw * 416 / 1536);
    overflow: hidden; border-radius: 11px; transition: height .38s ease;
}
.demo-card.is-expanded .demo-banner { height: calc(100cqw * 1024 / 1536); }
.demo-illustration {
    display: block; width: 100%; height: auto;
}
.demo-card .demo-arrow {
    position: absolute; right: 3px; top: calc(100cqw * 416 / 1536 - 3px); width: 34px; height: 34px;
    z-index: 1; cursor: pointer; text-decoration: none;
    transform: translateY(-100%); color: #0759b2; background: rgba(248, 252, 255, .96);
    border: 1px solid rgba(124, 183, 255, .55);
    animation: demo-arrow-pulse 10s ease-in-out infinite;
}
.demo-arrow:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }
@keyframes demo-arrow-pulse {
    0%, 100% {
        background-color: rgba(248, 252, 255, .96); color: #0759b2;
        border-color: rgba(124, 183, 255, .55);
        box-shadow: 0 0 0 0 rgba(12, 104, 207, 0);
    }
    50% {
        background-color: rgba(23, 56, 88, .96); color: #d9eaff;
        border-color: #638abb;
        box-shadow: 0 0 0 6px rgba(12, 104, 207, .16);
    }
}
@media (prefers-reduced-motion: reduce) {
    .demo-card .demo-arrow { animation: none; }
    .demo-card.q-card, .demo-banner, .projects-collapse { transition: none; }
}
.social-button {
    display: inline-flex; align-items: center; justify-content: center; gap: 10px;
    min-height: 30px; min-width: 124px; padding: 4px 16px;
    border-radius: 9px; color: white !important; text-decoration: none !important;
    font-size: 14px; font-weight: 650; box-shadow: var(--shadow);
    transition: filter .15s ease;
}
.social-button:hover { filter: brightness(1.1); }
.social-button:focus-visible { outline: 3px solid var(--blue); outline-offset: 3px; }
.linkedin-button { background: #0a66c2; }
.github-button { background: #192334; }
.social-button .q-btn__content { gap: 8px; }
.social-icon { width: 17px; height: 17px; flex: 0 0 auto; }

/* Use the logo blue for navigation, header controls and section headings in light mode. */
body:not(.body--dark) .nav-link:not(.active).q-btn,
body:not(.body--dark) .lang-button:not(.selected).q-btn,
body:not(.body--dark) .theme-toggle.q-btn,
body:not(.body--dark) .section-title { color: #1067cb; }

/* DARK THEME */
body.body--dark {
    color-scheme: dark;
    --ink: #e8f0ff;
    --muted: #b8c9e6;
    --blue: #7cb7ff;
    --line: #29466c;
    --card: #122743;
    --shadow: 0 7px 21px rgba(0, 8, 24, .22);
    color: var(--ink);
    background:
      radial-gradient(ellipse 56% 34% at 86% 67%, #112e50 0%, transparent 85%),
      linear-gradient(180deg, #081528 0%, #0c1d35 58%, #09182d 100%);
}
.body--dark .brand-mark { color: #7cb7ff; }
.body--dark .brand-divider { background: #47638a; }
.body--dark .nav-link.active.q-btn { color: #b4d6ff; background: #183b64; }
.body--dark .language-switch, .body--dark .theme-toggle.q-btn { border-color: var(--line); }
.body--dark .lang-button.q-btn { color: var(--muted); }
.body--dark .lang-button.selected.q-btn { color: white; background: #245d9e; box-shadow: none; }
.body--dark .theme-toggle.q-btn { background: var(--card); }
.body--dark .hero-shell { background: linear-gradient(120deg, #102440 10%, #143153 70%, #183c60 100%); }
.body--dark .hero-shell::before { opacity: .16; }
.body--dark .hero-eyebrow { color: #8ec2ff !important; }
.body--dark .hero-pitch { color: var(--ink) !important; }
.body--dark .primary-cta.q-btn { background: #1c63b3; }
.body--dark .secondary-cta.q-btn { color: #d9eaff; border-color: #629ee5; background: #142e4d; }
.body--dark .project-card.q-card, .body--dark .demo-card.q-card { background: var(--card); }
.body--dark .circle-arrow { color: #a8cfff; background: #1c3d63; }
.body--dark .demo-card .demo-arrow { color: #d9eaff; background: rgba(23, 56, 88, .96); border-color: #638abb; animation-delay: -1.9s; }
.body--dark .portrait-placeholder { border-color: #476b96; background: rgba(32, 67, 105, .3); }
.body--dark .placeholder-label { color: var(--muted); }
.body--dark .github-button { background: #203f65; }

@media (max-width: 1200px) {
    .nav-links { gap: 3px !important; }
    .nav-link.q-btn { padding: 0 7px; font-size: 14px; }
    .brand-name { font-size: 18px !important; }
    .brand { gap: 12px; }
}
/* Stack navigation before its labels crowd the brand and controls. */
@media (max-width: 1100px) {
    .header-inner { flex-wrap: wrap; padding: 4px 0; gap: 4px; }
    .nav-links { order: 3; width:100%; justify-content:space-between; }
    .nav-link.q-btn { min-height: 32px; }
}
@media (max-width: 980px) {
    :root { --hero-base-height: clamp(100px, 19svh, 170px); }
    .hero-inner { grid-template-columns: fit-content(72%) minmax(0, 1fr); }
}
/* Portrait tablets have room for larger previews beside each project title. */
@media (min-width: 601px) and (max-width: 980px) and (min-height: 800px) {
    .main-content { --preview-height: var(--demo-preview-height); }
    .demos-grid { grid-template-columns: 1fr; gap: 10px; }
    .projects-grid { grid-template-columns: 1fr; gap: 10px; }
    .project-card.q-card { width: 100%; max-width: none; display: grid; grid-template-columns: max-content minmax(0, 1fr); align-items: center; column-gap: 10px !important; }
    .project-image { height: 48px; max-height: 48px; aspect-ratio: auto; }
    .project-bottom { contain: none; padding: 0; }
}
@media (max-width: 600px) {
    :root { --hero-base-height: clamp(96px, 18svh, 144px); --section-gap: clamp(6px, 1.5svh, 16px); }
    .brand-mark { font-size: 28px !important; }
    .brand-name { font-size: 16px !important; }
    .brand-divider { height: 24px; }
    .lang-button.q-btn { min-height: 26px; min-width: 36px; font-size: 13px; }
    .header-controls { gap: 6px; }
    .theme-toggle.q-btn { width: 32px; min-width: 32px; height: 32px; }
    .nav-links { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 2px !important; align-items: stretch; }
    .nav-link.q-btn { font-size: 11px; padding: 2px; }
    .nav-link .q-btn__content { flex-direction: column; gap: 2px; }
    .nav-link .q-btn__content .block { max-width: 100%; overflow-wrap: anywhere; }
    .nav-link .q-icon { font-size: 16px; margin-right: 0; }
    .hero-inner { grid-template-columns: fit-content(calc(100% - var(--page-gutter))) minmax(0, 1fr); }
    .hero-copy { padding: 7px 0; }
    .hero-eyebrow { font-size: 10px !important; letter-spacing:.5px; }
    .hero-pitch { margin-top: 6px; font-size: 17px !important; }
    .hero-actions { gap: 8px !important; margin-top: 6px; }
    .cta.q-btn { font-size: 13px; padding: 0 11px; min-height: 34px; }
    .cta .q-icon { font-size: 18px; }
    .hero-portrait, .portrait-placeholder { opacity: .55; }
    .section-title { font-size: 18px; margin-bottom: 5px; }
    .projects-grid { grid-template-columns:1fr; gap: clamp(5px, 1svh, 10px); }
    .project-card.q-card { width: 100%; max-width: none; display: grid; grid-template-columns: max-content minmax(0, 1fr); align-items: center; column-gap: 8px !important; padding: 5px; border-radius: 12px; }
    .project-image { height: 33px; max-height: 33px; aspect-ratio: auto; border-radius: 7px; }
    .project-bottom { contain: none; padding: 0; min-height: 0; gap: 6px !important; }
    .project-title { font-size: 15px !important; }
    .circle-arrow { width: 26px; height: 26px; }
    .circle-arrow .q-icon { font-size: 17px; }
    .demos-grid { grid-template-columns: 1fr; }
    .demo-card.q-card { padding: 5px; border-radius: 12px; }
    .demo-banner { border-radius: 7px; }
    .social-button { min-width: 112px; padding: 3px 12px; font-size: 13px; }
}
@media (max-width: 360px) {
    :root { --page-gutter: 12px; --hero-base-height: 96px; }
    .brand-name { font-size: 14px !important; }
    .brand { gap: 8px; }
    .nav-link .q-icon, .cta .q-icon { display: none; }
    .nav-link.q-btn { font-size: 10px; letter-spacing: -.1px; }
    .hero-copy { padding: 6px 0; }
    .hero-eyebrow { font-size: 9px !important; letter-spacing: .3px; }
    .hero-pitch { font-size: 16px !important; }
    .hero-actions { margin-top: 5px; }
    .cta.q-btn { min-height: 30px; padding: 0 9px; font-size: 12px; }
    .section-title { font-size: 18px; }
    .project-title { font-size: 14px !important; }
}
@media (max-height: 680px) and (min-width: 601px) and (max-width: 1100px) {
    :root { --hero-base-height: clamp(96px, 19svh, 128px); --section-gap: 7px; --project-preview-limit: clamp(64px, calc(100svh - 450px), 200px); }
    .hero-copy { padding: 7px 0; }
    .hero-eyebrow { font-size: 11px !important; letter-spacing: .8px; }
    .hero-pitch { font-size: 17px !important; margin-top: 6px; }
    .hero-actions { margin-top: 6px; }
    .cta.q-btn { min-height: 36px; font-size: 14px; padding: 0 12px; }
}
/* Compact landscape layout keeps both sections within short viewports. */
@media (max-height: 540px) and (min-width: 601px) {
    :root { --hero-base-height: 84px; --section-gap: 5px; --project-preview-limit: clamp(48px, calc(100svh - 300px), 180px); --demo-preview-height: 54px; }
    .main-content { --project-preview-height: min(var(--project-preview-limit), calc(((100cqw - 2 * clamp(10px, 1.5vw, 20px)) / 3 - 14px) * 9 / 16)); }
    .header-inner { min-height: 42px; flex-wrap: nowrap; padding: 0; gap: 8px; }
    .brand { gap: 8px; }
    .brand-mark { font-size: 28px !important; }
    .nav-links { order: 0; width: auto; flex: 1; }
    .nav-link.q-btn { flex: 1 1 0; }
    .nav-link .q-btn__content .block { overflow-wrap: anywhere; }
    .hero-copy { padding: 6px 0; }
    .hero-eyebrow { font-size: 10px !important; letter-spacing: .6px; }
    .hero-pitch { font-size: 16px !important; margin-top: 4px; }
    .hero-actions { margin-top: 6px; }
    .cta.q-btn { min-height: 28px; font-size: 13px; padding: 0 12px; }
    .main-content { padding-bottom: 4px; }
    .section-title { font-size: 18px; margin-bottom: 6px; }
    .project-card.q-card { padding: 6px; }
    .project-bottom { min-height: 32px; padding-top: 5px; }
    .project-title { font-size: 13px !important; }
    .circle-arrow { width: 26px; height: 26px; }
}
@media (max-height: 540px) and (min-width: 601px) and (max-width: 1100px) {
    .brand-name, .brand-divider { display: none; }
    .nav-link.q-btn { font-size: 12px; padding: 0 5px; }
    .nav-link .q-icon { font-size: 17px; margin-right: 3px; }
}
@media (max-height: 400px) and (min-width: 601px) {
    :root { --hero-base-height: 74px; --section-gap: 4px; --project-preview-limit: clamp(36px, calc(100svh - 310px), 100px); --demo-preview-height: 44px; }
    .hero-copy { padding: 4px 0; }
    .hero-eyebrow { font-size: 9px !important; }
    .hero-pitch { font-size: 15px !important; margin-top: 3px; }
    .hero-actions { margin-top: 4px; }
    .social-button { min-height: 28px; padding-top: 2px; padding-bottom: 2px; font-size: 13px; }
    .section-title { font-size: 16px; margin-bottom: 4px; }
    .project-bottom { min-height: 28px; padding-top: 3px; }
    .project-title { font-size: 12px !important; }
}
@media (max-width: 600px) and (max-height: 600px) {
    :root { --hero-base-height: 88px; --section-gap: 4px; }
    .header-inner { gap: 3px; padding: 3px 0; }
    .nav-link.q-btn { min-height: 24px; font-size: 10px; }
    .nav-link .q-icon { display: none; }
    .hero-copy { padding: 4px 0; }
    .hero-eyebrow { font-size: 9px !important; letter-spacing: .2px; }
    .hero-pitch { margin-top: 3px; font-size: 15px !important; line-height: 1.25; }
    .hero-actions { margin-top: 4px; }
    .social-button { min-height: 28px; padding-top: 2px; padding-bottom: 2px; }
    .section-title { font-size: 16px; margin-bottom: 4px; }
    .projects-section { flex: initial; display: block; }
    .projects-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); grid-template-rows: auto; }
    .project-card.q-card { display: flex; padding: 5px; }
    .project-image { height: auto; min-height: 0; max-height: calc(clamp(28px, calc(100svh - 360px), 100px) * .75); }
    .project-bottom { padding: 4px 0 0; align-items: flex-start; }
    .project-title { font-size: 12px !important; }
    .project-card .circle-arrow { display: none; }
}
/* Small landscape phones need the same single-row header as wider phones. */
@media (max-width: 600px) and (min-width: 480px) and (max-height: 400px) {
    :root { --hero-base-height: 74px; --section-gap: 2px; }
    .header-inner { flex-wrap: nowrap; min-height: 38px; gap: 6px; padding: 2px 0; }
    .brand-name, .brand-divider { display: none; }
    .nav-links { order: 0; width: auto; flex: 1; }
    .nav-link.q-btn { font-size: 9px; }
    .hero-copy { padding: 3px 0; }
    .hero-pitch { font-size: 14px !important; }
    .section-title { margin-bottom: 3px; }
    .project-card.q-card, .demo-card.q-card { padding: 4px; }
}

/* The academic showcase now contains four equal project cards. */
@media (min-width: 1101px) {
    .projects-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
    .main-content {
        --project-preview-height: min(var(--project-preview-limit),
            calc(((100cqw - 3 * clamp(10px, 1.5vw, 20px)) / 4 - 16px) * 9 / 16));
    }
    .project-card.q-card { max-width: 90%; }
    .project-title { font-size: clamp(13px, 1.2vw, 18px) !important; }
}
@media (min-width: 601px) and (max-width: 1100px) {
    .projects-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .project-card.q-card { max-width: 90%; }
}
'''


SHOWCASE_CSS = r'''
/* Three independent homepage rows: business / research / academic. */
/* Reserve the scrollbar width when a preview opens/closes to prevent horizontal jitter. */
html { scrollbar-gutter: stable; }
.showcase-section { min-width: 0; }
.showcase-collapse {
    display: grid; grid-template-rows: 1fr; opacity: 1; visibility: visible;
    transition: grid-template-rows .35s ease, opacity .25s ease, visibility .35s;
}
.showcase-collapse-inner { min-height: 0; overflow: hidden; }
.main-content[data-active-row="business"] .showcase-section:not([data-showcase-row="business"]) .showcase-collapse,
.main-content[data-active-row="research"] .showcase-section:not([data-showcase-row="research"]) .showcase-collapse,
.main-content[data-active-row="academic"] .showcase-section:not([data-showcase-row="academic"]) .showcase-collapse {
    grid-template-rows: 0fr; opacity: 0; visibility: hidden; pointer-events: none;
}
/* A card in the middle/bottom row must not jump up when rows ABOVE it hide.
   Keep those rows' layout space, but fade away their cards; rows BELOW the
   hovered card still collapse completely, just like they do for the demos.
   This keeps the hit target stationary until the pointer actually leaves it. */
.main-content[data-active-row="research"] .showcase-section[data-showcase-row="business"] .showcase-collapse,
.main-content[data-active-row="academic"] .showcase-section[data-showcase-row="business"] .showcase-collapse,
.main-content[data-active-row="academic"] .showcase-section[data-showcase-row="research"] .showcase-collapse {
    grid-template-rows: 1fr;
}
.showcase-section .show-all { cursor: pointer; }
.showcase-section .show-all[aria-expanded="true"] { text-decoration: underline !important; }
/* Keep a consistent project-card language for academic work and research papers. */
.showcase-section .projects-grid {
    display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(10px, 1.5vw, 20px);
}
.showcase-section .research-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.showcase-section .project-card.q-card {
    container-type: inline-size; position: relative; display: flex; flex-direction: column;
    justify-self: stretch; align-self: start; width: 100%; max-width: none;
    min-width: 0; padding: 10px 12px; gap: 0 !important;
    border-radius: 14px; background: rgba(255,255,255,.62); border: 1px solid var(--line);
    box-shadow: var(--shadow); overflow: hidden;
    transition: border-color .2s ease, box-shadow .2s ease, background-color .2s ease;
}
.showcase-section .project-card.q-card:hover,
.showcase-section .project-card.q-card.is-hover-active,
.showcase-section .project-card.q-card:focus-within {
    border-color: var(--blue); box-shadow: 0 8px 24px rgba(12, 67, 139, .15);
}
.showcase-section .project-card-clickable { cursor: pointer; }
.showcase-section .project-bottom {
    contain: none; display: flex; justify-content: space-between; align-items: center;
    min-height: 38px; padding: 0; gap: 8px !important;
}
.showcase-section .project-title { min-width: 0; overflow-wrap: anywhere; font-size: clamp(13px, 1.2vw, 17px) !important; }
.showcase-section .project-image-reveal {
    width: 100%; max-height: 0; margin-top: 0; opacity: 0; overflow: hidden;
    border-radius: 10px; display: flex; align-items: center; justify-content: center;
    transition: max-height .38s ease, opacity .28s ease, margin-top .38s ease;
}
.showcase-section .project-card:hover .project-image-reveal,
.showcase-section .project-card.is-hover-active .project-image-reveal,
.showcase-section .project-card:focus-within .project-image-reveal {
    max-height: 270px; margin-top: 8px; opacity: 1;
}
.showcase-section .project-image {
    display: block; width: 100%; height: auto; max-width: 100%; max-height: 245px;
    aspect-ratio: 16 / 9; object-fit: contain; border-radius: 9px;
}
.showcase-section .project-image-placeholder {
    width: 100%; min-height: 140px; aspect-ratio: 16 / 9;
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
    color: #286eba; background: #e9f3ff; border: 1px solid var(--line); border-radius: 9px;
}
.showcase-section .project-image-placeholder .q-icon { font-size: 60px !important; }
.showcase-section .project-image-placeholder .q-label { font-size: 12px; font-weight: 650; }
.showcase-section .project-card .circle-arrow {
    opacity: 0; transform: translateX(-4px);
    transition: opacity .2s ease, transform .2s ease;
}
.showcase-section .project-card:hover .circle-arrow,
.showcase-section .project-card.is-hover-active .circle-arrow,
.showcase-section .project-card:focus-within .circle-arrow {
    opacity: 1; transform: translateX(0);
}
.showcase-section .project-card-overlay { z-index: 2; }
.research-figure-fallback { min-height: 160px; text-align: center; }
/* Use the same hover-to-reveal behavior for business demos, without an external JS file. */
.showcase-section .demo-card:hover .demo-banner,
.showcase-section .demo-card.is-hover-active .demo-banner,
.showcase-section .demo-card:focus-within .demo-banner { height: calc(100cqw * 1024 / 1536); }
.showcase-section .demo-card-clickable { cursor: pointer; }
.body--dark .showcase-section .project-card.q-card { background: var(--card); }
.body--dark .showcase-section .project-image-placeholder { background: #163555; color: #a8cfff; }
@media (max-width: 1100px) {
    .showcase-section .projects-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .showcase-section .research-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 600px) {
    .showcase-section .projects-grid,
    .showcase-section .research-grid { grid-template-columns: 1fr; }
    .showcase-section .project-card.q-card { display: flex; padding: 8px 10px; }
    .showcase-section .project-image { width: 100%; height: auto; max-height: 210px; }
    .showcase-section .project-bottom { min-height: 32px; }
    .showcase-section .project-title { font-size: 14px !important; }
    .showcase-section .project-card .circle-arrow { display: flex; }
}
@media (prefers-reduced-motion: reduce) {
    .showcase-collapse, .showcase-section .project-image-reveal { transition: none; }
}
'''

SHOWCASE_SCRIPT = r'''
<script>
/* Hover selection is transient: moving away from a card restores all rows.
   Use actual pointer movement (not pointerover/out) to ignore hover changes
   caused purely by the page reflowing when rows collapse. */
(() => {
    function main() { return document.querySelector('.main-content[data-active-row]'); }
    let hoveredCard = null;
    let keyboardCard = null;
    let keyboardNavigation = false;
    let selectedRow = null; // Explicitly selected via a "Show all" link.

    function cardRow(card) {
        return card?.closest('.showcase-section')?.dataset.showcaseRow || null;
    }
    function update() {
        const root = main();
        if (!root) return;
        root.dataset.activeRow = cardRow(hoveredCard) || cardRow(keyboardCard) || selectedRow || 'all';
        root.querySelectorAll('[data-showcase-toggle]').forEach(link => {
            link.setAttribute('aria-expanded', String(
                root.dataset.activeRow === link.dataset.showcaseToggle
            ));
        });
    }
    function hover(card) {
        if (card === hoveredCard) return;
        hoveredCard?.classList.remove('is-hover-active');
        hoveredCard = card;
        hoveredCard?.classList.add('is-hover-active');
        update();
    }
    function pointerMoved(event) {
        if (event.pointerType === 'touch') return;
        const root = main();
        if (!root) return;
        // elementFromPoint checks the current layout, including animated rows.
        const element = document.elementFromPoint(event.clientX, event.clientY);
        const card = element?.closest('.showcase-card') || null;
        const nextCard = card && root.contains(card) ? card : null;
        if (hoveredCard && hoveredCard !== nextCard) {
            // Restore the other rows on the first real movement outside the card.
            // Don't select a new card on the same event: restoring the layout can
            // otherwise cause rapid row switching while things animate.
            hover(null);
            return;
        }
        if (nextCard && !hoveredCard) hover(nextCard);
    }
    window.portfolioShowcase = {
        select: row => { selectedRow = row === 'all' ? null : row; update(); },
        toggle: row => { selectedRow = selectedRow === row ? null : row; update(); },
        reset: () => { selectedRow = null; keyboardCard = null; hover(null); },
    };
    document.addEventListener('pointermove', pointerMoved, {passive: true});
    document.addEventListener('pointerout', event => {
        // Leaving the browser/document altogether also clears transient hover.
        if (!event.relatedTarget) hover(null);
    });
    document.addEventListener('pointercancel', () => hover(null));
    window.addEventListener('blur', () => hover(null));
    document.addEventListener('pointerdown', () => {
        keyboardNavigation = false;
        keyboardCard = null; // Mouse clicks must not leave a sticky focus state.
        update();
    });
    document.addEventListener('focusin', event => {
        if (!keyboardNavigation) return;
        keyboardCard = event.target.closest?.('.showcase-card') || null;
        update();
    });
    document.addEventListener('focusout', () => {
        queueMicrotask(() => {
            if (!keyboardNavigation) return;
            keyboardCard = document.activeElement?.closest?.('.showcase-card') || null;
            update();
        });
    });
    document.addEventListener('click', event => {
        const toggle = event.target.closest?.('[data-showcase-toggle]');
        if (toggle) {
            event.preventDefault();
            window.portfolioShowcase.toggle(toggle.dataset.showcaseToggle);
        }
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
            window.portfolioShowcase.reset();
        } else if (event.key === 'Tab' || event.key.startsWith('Arrow')) {
            keyboardNavigation = true;
        }
    });
})();
</script>
'''

SOLUTION_CSS = r'''
/* Business demo pages extend the homepage's existing blue/white design. */
.solution-page { width: 100%; flex: 1; }
.solution-breadcrumb-row {
    width: min(var(--content-width), calc(100% - 2 * var(--page-gutter)));
    margin: 0 auto; min-height: 50px; display: flex; align-items: center;
    gap: 10px; font-size: 14px; color: var(--muted);
}
.solution-breadcrumb-link {
    display: inline-flex; align-items: center; gap: 6px; color: var(--blue) !important;
    font-weight: 600; text-decoration: none !important;
}
.solution-breadcrumb-link:hover { text-decoration: underline !important; }
.solution-breadcrumb-link:focus-visible, .solution-back:focus-visible {
    outline: 3px solid var(--blue); outline-offset: 4px; border-radius: 4px;
}
.solution-breadcrumb-chevron { opacity: .55; }
/* The illustration IS the page banner: one instance, exact homepage top crop. */
.solution-art-banner {
    width: 100%; padding: clamp(8px, 1.4vw, 18px) 0;
    background: linear-gradient(120deg, #edf5ff 0%, #e8f2ff 100%);
    border-top: 1px solid var(--line); border-bottom: 1px solid var(--line);
}
.solution-art-inner {
    width: min(1140px, calc(100% - 2 * var(--page-gutter)));
    margin: 0 auto;
}
.solution-visual-crop {
    position: relative; width: 100%; aspect-ratio: 1536 / 416;
    overflow: hidden; border-radius: 12px; background: #e9f3ff;
    border: 1px solid rgba(124, 183, 255, .32);
}
.solution-visual-crop .solution-visual-image {
    display: block; position: absolute; top: 0; left: 0;
    width: 100%; height: auto; max-width: none;
}
.solution-image-missing {
    display: flex; align-items: center; justify-content: center; height: 100%;
    text-align: center; font-size: 14px; color: var(--muted); padding: 16px;
}
.solution-content {
    width: min(1140px, calc(100% - 2 * var(--page-gutter)));
    margin: 0 auto; padding: clamp(18px, 3vw, 36px) 0 64px;
}
/* The coming-soon announcement is the primary hero, not an alert strip. */
.solution-status {
    position: relative; overflow: hidden;
    width: 100%; min-height: 380px; padding: clamp(30px, 4.6vw, 62px);
    display: flex; justify-content: center; align-items: center;
    text-align: center; isolation: isolate;
    background: linear-gradient(132deg, #f7fbff 0%, #e9f3ff 52%, #dcecff 100%);
    border: 1px solid #b6d4f8; border-radius: 21px;
    box-shadow: 0 12px 38px rgba(49, 86, 153, .10);
}
.solution-status::before {
    content: ''; position: absolute; z-index: -1; pointer-events: none;
    width: 560px; height: 560px; right: -340px; top: -360px;
    border-radius: 50%; border: 85px solid rgba(50, 120, 220, .065);
}
.solution-status-inner { width: 100%; max-width: 790px; }
.solution-project-label {
    color: #0a5dbd; font-size: 15px; font-weight: 800; letter-spacing: 1.9px;
    text-transform: uppercase;
}
.solution-kicker {
    display: block; margin-top: 5px; color: var(--muted);
    font-size: 13px; font-weight: 600; letter-spacing: .4px;
}
.solution-status-icon {
    width: 66px; height: 66px; margin: 23px auto 17px;
    display: flex; justify-content: center; align-items: center;
    border-radius: 19px; color: #075ebd; background: #d1e5ff;
    border: 1px solid #b3d2fa; box-shadow: 0 5px 18px rgba(10, 90, 175, .11);
}
.solution-status-icon .q-icon { font-size: 34px !important; }
.solution-status-title {
    margin: 0; color: var(--ink); font-size: clamp(42px, 5.6vw, 72px);
    font-weight: 800; letter-spacing: -2.4px; line-height: 1.09;
}
.solution-coming {
    display: block; margin-top: 10px; font-size: clamp(20px, 2.8vw, 29px);
    line-height: 1.2; color: #0b60bd; font-weight: 740;
}
.solution-status-note {
    display: block; margin: 15px auto 0; max-width: 640px;
    color: var(--muted); font-size: 15px; line-height: 1.6;
}
.solution-status-lead {
    display: block; margin: 20px auto 0; max-width: 740px;
    padding-top: 18px; border-top: 1px solid rgba(47, 112, 189, .18);
    color: var(--ink); font-size: clamp(17px, 1.9vw, 21px); line-height: 1.5;
}
.solution-section-heading {
    display: block; margin: 36px 0 10px;
    font-size: clamp(24px, 2.8vw, 31px); line-height: 1.25;
    letter-spacing: -.85px; font-weight: 750; color: var(--ink);
}
.solution-section-intro {
    display: block; max-width: 910px; color: var(--muted);
    font-size: 16px; line-height: 1.75;
}
.solution-steps { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; margin-top: 20px; }
.solution-step {
    min-width: 0; min-height: 176px; padding: 23px;
    border-radius: 15px; border: 1px solid var(--line);
    background: rgba(255,255,255,.65); box-shadow: var(--shadow);
}
.solution-step-number {
    width: 34px; height: 34px; display: flex; justify-content: center; align-items: center;
    margin-bottom: 17px; border-radius: 11px; background: #e5f1ff;
    color: #1167ca; font-size: 13px; font-weight: 800;
}
.solution-step-title { font-size: 18px; font-weight: 720; color: var(--ink); line-height: 1.25; }
.solution-step-copy { margin-top: 9px; font-size: 14px; color: var(--muted); line-height: 1.65; }
.solution-example {
    display: flex; align-items: flex-start; gap: 14px; margin-top: 24px;
    border-radius: 14px; border: 1px solid var(--line);
    padding: 20px 23px; background: #eaf3ff;
}
.solution-example-icon { color: #1167ca; font-size: 23px; }
.solution-example-title { font-size: 15px; font-weight: 740; color: var(--ink); }
.solution-example-copy { margin-top: 5px; font-size: 14px; line-height: 1.65; color: var(--muted); }
.solution-actions { display: flex; margin-top: 36px; }
.solution-back.q-btn {
    background: #116bcf; color: #fff; border-radius: 10px;
    padding: 0 20px; min-height: 44px; font-weight: 650;
}
/* Dark pages follow the homepage's shared dark palette. */
.body--dark .solution-art-banner {
    background: linear-gradient(120deg, #112740 0%, #153355 100%);
    border-color: var(--line);
}
.body--dark .solution-visual-crop { background: #163555; border-color: #29466c; }
.body--dark .solution-status {
    background: linear-gradient(132deg, #102540 0%, #153555 56%, #1b4672 100%);
    border-color: #325983; box-shadow: 0 12px 38px rgba(0, 8, 24, .25);
}
.body--dark .solution-status::before { border-color: rgba(154, 200, 255, .07); }
.body--dark .solution-project-label, .body--dark .solution-coming { color: #9ccbff; }
.body--dark .solution-status-icon { background: #21456c; color: #b6d7ff; border-color: #3b658f; }
.body--dark .solution-status-lead { border-color: rgba(164, 205, 255, .2); }
.body--dark .solution-step { background: var(--card); }
.body--dark .solution-example { background: #173452; }
.body--dark .solution-example-icon { color: #91c5ff; }
.body--dark .solution-back.q-btn { background: #1c63b3; }
@media (max-width: 700px) {
    .solution-breadcrumb-row { min-height: 44px; font-size: 12px; }
    .solution-art-banner { padding: 8px 0; }
    .solution-visual-crop { border-radius: 9px; }
    .solution-status { min-height: 335px; padding: 28px 18px; border-radius: 15px; }
    .solution-status-icon { width: 54px; height: 54px; margin: 18px auto 14px; }
    .solution-status-icon .q-icon { font-size: 29px !important; }
    .solution-status-title { letter-spacing: -1.7px; }
    .solution-status-lead { margin-top: 18px; padding-top: 15px; }
    .solution-steps { grid-template-columns: 1fr; gap: 11px; }
    .solution-step { min-height: unset; padding: 19px; }
    .solution-step-number { margin-bottom: 11px; }
    .solution-content { padding-bottom: 36px; }
}
'''



# ---------------------------------------------------------------------------
# Convex DeepStack research paper — embedded, no external styles.css required
# ---------------------------------------------------------------------------
RESEARCH_PROJECT = {
    'category': 'research',
    'domain': {'en': 'Trustworthy AI', 'fr': 'IA de confiance'},
    'title': {
        'en': 'Convex DeepStack: More Reliable Deep Learning',
        'fr': 'Convex DeepStack : un deep learning plus fiable',
    },
    'pitch': {
        'en': ('Co-developed a framework for reliable deep networks that jointly optimizes '
               'accuracy, speed and resilience to corrupted data.'),
        'fr': ('Co-développement d’un cadre pour des réseaux profonds plus fiables, qui '
               'optimise conjointement précision, rapidité et robustesse face aux données corrompues.'),
    },
    'skills': [
        {'en': 'Neural Networks',        'fr': 'Réseaux de neurones',       'icon': 'psychology'},
        {'en': 'Convex Optimization',    'fr': 'Optimisation convexe',      'icon': 'functions'},
        {'en': 'Automated ML',           'fr': 'ML automatisé',             'icon': 'auto_awesome'},
        {'en': 'Robust ML',              'fr': 'ML robuste',                'icon': 'verified_user'},
        {'en': 'Bayesian Optimization',  'fr': 'Optimisation bayésienne',   'icon': 'tune'},
        {'en': 'Conformal Methods',      'fr': 'Méthodes conformes',        'icon': 'rule'},
        {'en': 'Model Evaluation',       'fr': 'Évaluation de modèles',     'icon': 'bar_chart'},
        {'en': 'Python',                 'fr': 'Python',                    'icon': 'code'},
    ],
    'overview': {
        'en': ('Deep networks can be unpredictable to train, while reliably optimized alternatives '
               'are usually shallow. This research bridges that gap by combining independently '
               'optimized building blocks into an adaptive, deeper predictor.'),
        'fr': ('Les réseaux profonds sont parfois imprévisibles à entraîner, alors que les approches '
               'plus stables restent souvent peu profondes. Cette recherche comble cet écart en '
               'assemblant des blocs optimisés séparément dans un prédicteur plus profond et adaptable.'),
    },
    'methodology': {
        'en': ('Designed a residual-stacking strategy using standard and robust convex neural blocks. '
               'Combined Bayesian hyperparameter search with a conformal early-stop rule, then benchmarked '
               'prediction error, corruption robustness and search time against three baselines.'),
        'fr': ('Conception d’une stratégie d’empilement résiduel à partir de blocs neuronaux convexes, '
               'standards et robustes. Association d’une recherche bayésienne des hyperparamètres à un '
               'arrêt anticipé conforme, puis comparaison avec trois méthodes de référence.'),
    },
    'key_result': {
        'value': '14.03×',
        'caption': {
            'en': 'lower combined mmMSE-time score than the next-best baseline.',
            'fr': 'score combiné mmMSE-temps inférieur à la meilleure baseline suivante.',
        },
        'secondary': {
            'en': 'Score 6.07 at 40% corruption',
            'fr': 'Score 6,07 à 40 % de corruption',
        },
    },
    'banner_illustration': 'banner_illustration.png',
    'figure': {
        'file': 'figure6_accuracy_cost_zoom.png',
        'caption': {
            'en': 'Figure 6 · Prediction error vs. search time',
            'fr': 'Figure 6 · Erreur de prédiction vs temps de recherche',
        },
    },
    'report_url': '/assets/project_report.pdf',
    'code_url': None,
}

RESEARCH_TEXT = {
    'en': {
        'home': 'Home', 'academic': 'Academic Projects', 'research': 'Research Papers',
        'industrial': 'Real Life Projects', 'about': 'About',
        'academic_label': 'Academic project', 'research_label': 'Research paper',
        'industrial_label': 'Industrial project', 'report': 'Read research paper',
        'code': 'View code', 'skills': 'Skills Demonstrated', 'overview': 'Research Overview',
        'methodology': 'Methodology', 'result': 'Key Result', 'no_link': 'Link not supplied',
    },
    'fr': {
        'home': 'Accueil', 'academic': 'Projets académiques', 'research': 'Articles de recherche',
        'industrial': 'Projets professionnels', 'about': 'À propos',
        'academic_label': 'Projet académique', 'research_label': 'Article de recherche',
        'industrial_label': 'Projet industriel', 'report': 'Lire l’article',
        'code': 'Voir le code', 'skills': 'Compétences mobilisées', 'overview': 'Enjeu de recherche',
        'methodology': 'Méthodologie', 'result': 'Résultat clé', 'no_link': 'Lien non renseigné',
    },
}

PROJECT_IMAGES = ['driving-planning.svg', 'eeg-decoding.svg', 'rocket-landing.svg', 'ball-valve-anomaly.svg']
DEMO_IMAGES = [
    ('clip', 'PartFinder illustration.png'),
    ('flowdesk', 'FlowDesk illustration.jpg'),
    ('procurematch', 'ProcureMatch illustration.png'),
]
DEMO_ROUTES = {'clip': '', 'flowdesk': '/flowdesk', 'procurematch': '/procurematch'}
NAV_ICONS = ['home', 'svguse:/assets/microchip-ai.svg#microchip-ai', 'school', 'article', 'person_outline']

# Copy is deliberately written in terms of planned capabilities, not shipped features.
SOLUTION_COPY = {
    'flowdesk': {
        'EN': {
            'kicker': 'Service operations  •  workflow automation',
            'lead': 'From incoming service requests to clear ownership, timely follow-up and actionable visibility.',
            'summary_title': 'A more organized way to handle internal requests',
            'summary': (
                'FlowDesk is designed to bring service requests into a single, trackable process. '
                'The upcoming demo will show how requests can be automatically categorized and routed, '
                'how teams can manage work in one shared queue, and how managers can spot backlog, '
                'priorities and overdue items before they become bottlenecks.'
            ),
            'steps_title': 'What the interactive demo will show',
            'steps': [
                ('Submit & route', 'Create a service request and see it categorized, prioritized and assigned to a team through an automated workflow.'),
                ('Manage the queue', 'Search and filter incoming work, update request status, and keep a traceable history of who changed what.'),
                ('Track service performance', 'Explore a dashboard for backlog, overdue requests, priority mix and scheduled operational summaries.'),
            ],
            'example_title': 'Business value',
            'example': 'For operations and internal service teams: less manual triage, fewer missed follow-ups, and clearer accountability from intake through resolution.',
        },
        'FR': {
            'kicker': 'Opérations de service  •  automatisation des workflows',
            'lead': 'Des demandes entrantes à une prise en charge claire, un suivi fiable et une meilleure visibilité.',
            'summary_title': 'Une gestion plus fluide des demandes internes',
            'summary': (
                'FlowDesk vise à centraliser les demandes dans un processus traçable. '
                'La future démo montrera comment catégoriser et orienter automatiquement les demandes, '
                'gérer les tâches dans une file partagée et suivre les priorités, le volume en attente '
                'et les retards pour éviter les blocages.'
            ),
            'steps_title': 'Ce que présentera la démo interactive',
            'steps': [
                ('Soumettre et orienter', 'Créer une demande puis voir sa catégorisation, sa priorisation et son attribution automatiques.'),
                ('Gérer la file', 'Rechercher et filtrer les demandes, modifier leur statut et conserver un historique des actions.'),
                ('Piloter les opérations', 'Consulter des indicateurs sur les demandes en attente, les retards, les priorités et les rapports réguliers.'),
            ],
            'example_title': 'Valeur métier',
            'example': 'Pour les équipes de support et les opérations : moins de tri manuel, moins de relances oubliées et une meilleure traçabilité du traitement.',
        },
    },
    'procurematch': {
        'EN': {
            'kicker': 'Procurement & finance  •  document automation',
            'lead': 'Catch invoice discrepancies before approval, without reviewing every document line by line.',
            'summary_title': 'Turn supplier documents into review-ready exceptions',
            'summary': (
                'ProcureMatch is designed to help purchasing and finance teams reconcile supplier invoices '
                'against purchase orders. The upcoming demo will use document extraction to capture invoice '
                'details, compare suppliers, quantities and unit prices, and flag differences that need '
                'human review — with a clear record of each decision.'
            ),
            'steps_title': 'What the interactive demo will show',
            'steps': [
                ('Capture the invoice', 'Upload an invoice, inspect OCR-extracted header and line items, and correct fields that need attention.'),
                ('Compare with the PO', 'Match the invoice to the purchase order and highlight price, quantity or reference discrepancies.'),
                ('Review & report', 'Route exceptions for human approval or rejection, retain an audit trail, and explore supplier variance summaries.'),
            ],
            'example_title': 'Example business scenario',
            'example': 'An invoice lists 10 chairs at CHF 135 each, while the purchase order specifies CHF 120. ProcureMatch will flag the CHF 150 price variance for review — never automatically approving the payment.',
        },
        'FR': {
            'kicker': 'Achats & finance  •  automatisation documentaire',
            'lead': 'Repérer les écarts de facturation avant validation, sans vérifier chaque ligne manuellement.',
            'summary_title': 'Transformer les factures en exceptions à examiner',
            'summary': (
                'ProcureMatch vise à aider les équipes achats et finance à rapprocher les factures '
                'fournisseurs des bons de commande. La future démo présentera l’extraction des données '
                'des factures, la comparaison des fournisseurs, quantités et prix unitaires, ainsi que '
                'la détection des écarts nécessitant une validation humaine et traçable.'
            ),
            'steps_title': 'Ce que présentera la démo interactive',
            'steps': [
                ('Lire la facture', 'Importer une facture, vérifier les champs extraits par OCR et corriger les données incertaines.'),
                ('Rapprocher la commande', 'Comparer les prix, quantités et références de la facture avec le bon de commande.'),
                ('Décider et suivre', 'Soumettre les écarts à validation humaine, conserver une piste d’audit et consulter les synthèses par fournisseur.'),
            ],
            'example_title': 'Exemple métier',
            'example': 'Une facture indique 10 chaises à CHF 135 pièce, alors que le bon de commande prévoit CHF 120. ProcureMatch signalera un écart de CHF 150 à examiner, sans approuver automatiquement le paiement.',
        },
    },
}

PAGE_LABELS = {
    'EN': {
        'breadcrumb': 'Business solutions',
        'status_title': 'Work in progress',
        'status_soon': 'Coming soon',
        'status_note': 'The interactive demo is being developed. Here is what you will be able to explore.',
        'back': 'Back to business solutions',
        'missing_art': 'Add the original illustration to the assets folder to display this preview.',
    },
    'FR': {
        'breadcrumb': 'Solutions professionnelles',
        'status_title': 'En cours de réalisation',
        'status_soon': 'Bientôt disponible',
        'status_note': 'La démo interactive est en développement. Voici les fonctionnalités prévues.',
        'back': 'Retour aux solutions professionnelles',
        'missing_art': 'Ajoutez l’illustration d’origine dans le dossier assets pour afficher cet aperçu.',
    },
}


# ---------------------------------------------------------------------------
# EEG academic project page — fully embedded in main.py (no app.py dependency)
# ---------------------------------------------------------------------------
EEG_PROJECT = {
    'category': 'academic',
    'domain': {'en': 'Biomedical AI', 'fr': 'IA biomédicale'},
    'title': {
        'en': 'Neural Networks for EEG Seizure Detection',
        'fr': 'Détection de crises épileptiques par IA',
    },
    'pitch': {
        'en': ('Built a frequency-based EEG classifier and co-evaluated four neural approaches '
               'to identify seizures in brain recordings. The study explores whether linking '
               'electrodes spatially improves detection.'),
        'fr': ('J’ai développé un classifieur EEG fréquentiel et comparé en équipe '
               'quatre modèles neuronaux pour détecter les crises épileptiques et '
               'évaluer l’apport des liens entre électrodes.'),
    },
    'skills': [
        {'en': 'Signal Processing',       'fr': 'Traitement du signal',     'icon': 'graphic_eq'},
        {'en': 'Neural Networks',         'fr': 'Réseaux de neurones',     'icon': 'psychology'},
        {'en': 'Feature Engineering',     'fr': 'Création de variables',   'icon': 'tune'},
        {'en': 'Model Evaluation',        'fr': 'Évaluation de modèles',   'icon': 'assessment'},
        {'en': 'Cross-Validation',        'fr': 'Validation croisée',     'icon': 'fact_check'},
        {'en': 'PyTorch',                 'fr': 'PyTorch',                 'icon': 'memory'},
        {'en': 'Python',                  'fr': 'Python',                  'icon': 'code'},
        {'en': 'Research Collaboration',  'fr': 'Collaboration',    'icon': 'groups'},
    ],
    'overview': {
        'en': ('Manually reviewing EEG recordings to spot seizures is time-consuming. '
               'Our team compared four neural models for classifying 12-second EEG segments, '
               'including methods that account for how scalp electrodes are positioned.'),
        'fr': ('Repérer des crises dans de longs enregistrements EEG demande une analyse '
               'manuelle chronophage. Notre équipe a comparé quatre modèles neuronaux pour '
               'classer des séquences EEG de 12 secondes, dont des approches tenant compte '
               'de la position des électrodes.'),
    },
    'methodology': {
        'en': ('I implemented the frequency-domain CNN–BiLSTM pipeline, transforming '
               'filtered EEG signals into spectral features. We harmonized data preprocessing '
               'and compared all four architectures through five-fold cross-validation '
               'on the TUSZ dataset.'),
        'fr': ('J’ai développé le modèle CNN–BiLSTM en domaine fréquentiel, à partir '
               'de signaux EEG filtrés et convertis en caractéristiques spectrales. '
               'Nous avons uniformisé le prétraitement et comparé quatre architectures '
               'par validation croisée à cinq plis sur TUSZ.'),
    },
    'key_result': {
        'value': '0.872',
        'caption': {
            'en': 'ROC AUC achieved by the best model, a Graph Transformer (higher is better).',
            'fr': 'ROC AUC du meilleur modèle, un Graph Transformer (plus élevé = meilleur).',
        },
        'secondary': {
            'en': 'Macro-F1 0.790 · 5-fold CV',
            'fr': 'Macro-F1 0,790 · 5 plis',
        },
    },
    'banner_illustration': 'eeg-decoding.png',
    'figure': {
        'file': 'roc_auc_model_comparison.svg',
        'caption': {
            'en': 'ROC AUC · paper Tables 2–3',
            'fr': 'ROC AUC · tableaux 2–3',
        },
    },
    'report_url': '/assets/project_report.pdf',
    'code_url': None,
}


EEG_TEXT = {
    'en': {
        'home': 'Home', 'academic': 'Academic Projects', 'research': 'Research Papers',
        'industrial': 'Real Life Projects', 'about': 'About',
        'academic_label': 'Academic project', 'research_label': 'Research paper',
        'industrial_label': 'Industrial project', 'report': 'Read project report',
        'code': 'View code', 'skills': 'Skills Demonstrated', 'overview': 'Project Overview',
        'methodology': 'Methodology', 'result': 'Key Result', 'no_link': 'Link not supplied',
    },
    'fr': {
        'home': 'Accueil', 'academic': 'Projets académiques', 'research': 'Articles de recherche',
        'industrial': 'Projets professionnels', 'about': 'À propos',
        'academic_label': 'Projet académique', 'research_label': 'Article de recherche',
        'industrial_label': 'Projet industriel', 'report': 'Lire le rapport',
        'code': 'Voir le code', 'skills': 'Compétences mobilisées', 'overview': 'Présentation du projet',
        'methodology': 'Méthodologie', 'result': 'Résultat clé', 'no_link': 'Lien non renseigné',
    },
}


def eeg_localized(value: object, lang: str) -> str:
    """Return an English/French value without changing research content."""
    if isinstance(value, dict):
        return str(value.get(lang) or value.get('en') or '')
    return '' if value is None else str(value)


EEG_CSS = r'''
/* Extends the main portfolio's typography, variables and light/dark palette. */
.eeg-page { width: 100%; min-width: 0; flex: 1; }
.eeg-container { width: min(1180px, calc(100% - 2 * var(--page-gutter))); margin: 0 auto; }
.eeg-breadcrumb { min-height: 52px; }
.eeg-hero-section {
    background: linear-gradient(120deg, #f6faff 10%, #edf5ff 70%, #e5f1ff 100%);
    border-block: 1px solid var(--line);
    overflow: hidden;
}
.eeg-hero-inner {
    display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(260px, .8fr);
    gap: clamp(20px, 4vw, 58px); align-items: center;
    padding-block: clamp(32px, 5.4vw, 74px);
}
.eeg-hero-copy { min-width: 0; }
.eeg-eyebrow {
    display: flex; flex-wrap: wrap; gap: 9px; align-items: center;
    color: #0866cc; font-size: 12px; letter-spacing: 1.15px; font-weight: 760;
    text-transform: uppercase;
}
.eeg-eyebrow-divider { opacity: .5; }
.eeg-title {
    margin: 14px 0 14px; color: var(--ink);
    font-size: clamp(31px, 4.25vw, 56px); font-weight: 800;
    line-height: 1.1; letter-spacing: -1.8px;
}
.eeg-pitch { max-width: 730px; font-size: clamp(15px, 1.55vw, 18px); line-height: 1.7; color: var(--muted); }
.eeg-actions { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-top: 26px; }
.eeg-report-button.q-btn {
    min-height: 44px; padding: 0 18px; font-size: 14px; font-weight: 680;
    border-radius: 10px; background: #116bcf; color: white; box-shadow: none;
}
.eeg-report-note { color: var(--muted); font-size: 13px; line-height: 1.5; }
.eeg-hero-visual {
    width: 100%; min-width: 0; min-height: 240px; aspect-ratio: 4 / 3;
    display: flex; align-items: center; justify-content: center; overflow: hidden;
    border: 1px solid var(--line); border-radius: 20px;
    background: rgba(255,255,255,.66); box-shadow: var(--shadow);
}
.eeg-hero-image { width: 100%; height: 100%; object-fit: contain; display: block; }
.eeg-visual-fallback {
    display: flex; flex-direction: column; gap: 12px; align-items: center;
    justify-content: center; color: #116bcf;
}
.eeg-visual-icon { font-size: 96px !important; opacity: .65; }
.eeg-visual-caption { font-size: 13px; font-weight: 750; letter-spacing: 2px; }
.eeg-content { padding-top: clamp(24px, 3.5vw, 46px); padding-bottom: 70px; }
.eeg-panel {
    border: 1px solid var(--line); border-radius: 17px;
    background: rgba(255,255,255,.66); box-shadow: var(--shadow);
}
.eeg-skills-panel { padding: clamp(19px, 2.4vw, 29px); }
.eeg-section-header { display: flex; align-items: center; gap: 18px; margin-bottom: 18px; }
.eeg-section-heading { margin: 0; font-size: clamp(17px, 1.8vw, 22px); font-weight: 750; color: var(--ink); letter-spacing: -.4px; }
.eeg-section-rule { height: 1px; background: var(--line); flex: 1; }
.eeg-skill-tags { display: flex; flex-wrap: wrap; gap: 9px; }
.eeg-skill-tag {
    display: inline-flex; align-items: center; gap: 7px; min-height: 36px;
    padding: 7px 12px; border-radius: 999px; color: #1458a6;
    font-weight: 600; font-size: 13px; line-height: 1.2;
    border: 1px solid #c5dbfb; background: #eaf3ff;
}
.eeg-skill-tag .q-icon { font-size: 17px; }
.eeg-details { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin-top: 18px; }
.eeg-detail-card { min-width: 0; padding: clamp(22px, 2.8vw, 32px); }
.eeg-card-heading { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.eeg-card-icon {
    width: 40px; height: 40px; flex: 0 0 auto;
    display: flex; align-items: center; justify-content: center;
    border-radius: 12px; background: #e5f1ff; color: #1167ca;
}
.eeg-card-icon .q-icon { font-size: 23px; }
.eeg-card-title { color: var(--ink); font-size: clamp(17px, 1.7vw, 21px); font-weight: 750; letter-spacing: -.3px; }
.eeg-card-copy { color: var(--muted); font-size: 15px; line-height: 1.8; }
.eeg-result-card { grid-column: 1 / -1; }
.eeg-result-layout { display: grid; grid-template-columns: minmax(0, 1fr) minmax(240px, 1fr); gap: 28px; align-items: center; }
.eeg-result-value { color: #0a62c5; font-size: clamp(47px, 5.5vw, 74px); font-weight: 820; line-height: 1.06; letter-spacing: -2.6px; }
.eeg-result-caption { margin-top: 10px; max-width: 490px; color: var(--muted); font-size: 15px; line-height: 1.65; }
.eeg-result-pill {
    display: inline-flex; gap: 7px; align-items: center;
    margin-top: 16px; padding: 7px 12px; border-radius: 999px;
    color: #1458a6; background: #eaf3ff; border: 1px solid #c5dbfb;
    font-weight: 640; font-size: 13px;
}
.eeg-result-pill .q-icon { font-size: 16px; }
.eeg-figure-side { min-width: 0; padding: 14px; border-radius: 13px; background: #f2f7ff; border: 1px solid var(--line); }
.eeg-result-figure { width: 100%; height: auto; max-height: 280px; object-fit: contain; }
.eeg-figure-caption { margin-top: 8px; font-size: 12px; color: var(--muted); }
.eeg-meter-title { font-size: 14px; font-weight: 780; color: var(--ink); }
.eeg-meter-track { width: 100%; height: 18px; margin-top: 22px; border-radius: 999px; background: #d6e6fc; overflow: hidden; }
.eeg-meter-fill { height: 100%; border-radius: inherit; background: #116bcf; }
.eeg-meter-axis { display: flex; justify-content: space-between; margin-top: 9px; color: var(--muted); font-size: 12px; }
.eeg-back-row { display: flex; margin-top: 28px; }
.eeg-back-button.q-btn { min-height: 42px; border-radius: 10px; background: #116bcf; color: #fff; font-weight: 650; padding: 0 18px; }
.eeg-page a:focus-visible { outline: 3px solid var(--blue); outline-offset: 4px; }

/* Use the exact dark-theme palette that the homepage toggles. */
.body--dark .eeg-hero-section { background: linear-gradient(120deg, #102440 10%, #143153 70%, #183c60 100%); }
.body--dark .eeg-eyebrow { color: #8ec2ff; }
.body--dark .eeg-hero-visual, .body--dark .eeg-panel { background: var(--card); }
.body--dark .eeg-visual-fallback { color: #8ec2ff; }
.body--dark .eeg-skill-tag, .body--dark .eeg-result-pill { color: #b6d7ff; background: #1c3d63; border-color: #365d88; }
.body--dark .eeg-card-icon { background: #21456c; color: #b6d7ff; }
.body--dark .eeg-result-value { color: #9ccbff; }
.body--dark .eeg-figure-side { background: #122c49; }
.body--dark .eeg-meter-track { background: #284a70; }
.body--dark .eeg-meter-fill { background: #7cb7ff; }
.body--dark .eeg-report-button.q-btn, .body--dark .eeg-back-button.q-btn { background: #1c63b3; }
@media (max-width: 780px) {
    .eeg-hero-inner { grid-template-columns: 1fr; gap: 24px; padding-block: 26px; }
    .eeg-hero-visual { min-height: 180px; max-height: 320px; aspect-ratio: 16 / 9; }
    .eeg-details { grid-template-columns: 1fr; gap: 13px; }
    .eeg-result-layout { grid-template-columns: 1fr; gap: 20px; }
}
@media (max-width: 480px) {
    .eeg-title { font-size: 32px; letter-spacing: -1px; }
    .eeg-hero-visual { min-height: 150px; }
    .eeg-skill-tags { gap: 7px; }
    .eeg-skill-tag { font-size: 12px; padding: 6px 9px; }
    .eeg-detail-card { padding: 20px; }
    .eeg-content { padding-bottom: 36px; }
}
'''


def render_eeg_content(lang: str, assets_dir: Path, asset_url: Callable[[str], str],
                       academic_url: str) -> None:
    """Render the EEG route inside main.py's existing site layout/theme.

    asset_url is provided by main.py so project assets retain its cache-busting.
    Missing optional imagery/figures/report degrade gracefully, not as broken links.
    """
    t = EEG_TEXT[lang]
    project_title = eeg_localized(EEG_PROJECT['title'], lang)
    back_text = t['academic']
    missing_report = ('Le rapport sera disponible après ajout du PDF.' if lang == 'fr'
                      else 'The report link will appear when the PDF is added.')

    with ui.element('main').classes('eeg-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=academic_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(back_text)
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['academic_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(eeg_localized(EEG_PROJECT['domain'], lang))
                    ui.html(project_title, tag='h1').classes('eeg-title')
                    ui.label(eeg_localized(EEG_PROJECT['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        report_file = assets_dir / EEG_PROJECT['report_url'].rsplit('/', 1)[-1]
                        if report_file.is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(EEG_PROJECT['report_url'], new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label(missing_report).classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner_name = next((name for name in (EEG_PROJECT['banner_illustration'], 'eeg-decoding.svg')
                                        if (assets_dir / name).is_file()), None)
                    if banner_name:
                        ui.element('img').props(
                            f'src="{asset_url(banner_name)}" alt="EEG signal analysis illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('monitor_heart').classes('eeg-visual-icon')
                            ui.label('EEG  ·  AI').classes('eeg-visual-caption')

        with ui.element('div').classes('eeg-container eeg-content'):
            with ui.element('section').classes('eeg-panel eeg-skills-panel'):
                with ui.element('div').classes('eeg-section-header'):
                    ui.html(t['skills'], tag='h2').classes('eeg-section-heading')
                    ui.element('span').classes('eeg-section-rule')
                with ui.element('div').classes('eeg-skill-tags'):
                    for skill in EEG_PROJECT['skills']:
                        with ui.element('div').classes('eeg-skill-tag'):
                            ui.icon(skill['icon']).props('aria-hidden=true')
                            ui.label(eeg_localized(skill, lang))

            with ui.element('div').classes('eeg-details'):
                for key, icon in (('overview', 'device_hub'), ('methodology', 'gps_fixed')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(eeg_localized(EEG_PROJECT[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('table_chart').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(EEG_PROJECT['key_result']['value']).classes('eeg-result-value')
                            ui.label(eeg_localized(EEG_PROJECT['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(eeg_localized(EEG_PROJECT['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure_filename = EEG_PROJECT['figure']['file']
                            if (assets_dir / figure_filename).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure_filename)}" alt="ROC AUC model comparison" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(eeg_localized(EEG_PROJECT['figure']['caption'], lang)).classes('eeg-figure-caption')
                            else:
                                # Show only the sourced best-model ROC AUC. Do not invent other model metrics.
                                ui.label('ROC AUC').classes('eeg-meter-title')
                                with ui.element('div').classes('eeg-meter-track').props('role=img aria-label="ROC AUC 0.872 out of 1"'):
                                    ui.element('div').classes('eeg-meter-fill').style(
                                        f'width: {100 * float(EEG_PROJECT["key_result"]["value"]):.1f}%'
                                    )
                                with ui.element('div').classes('eeg-meter-axis'):
                                    ui.label('0.0')
                                    ui.label('1.0')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(back_text, icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(academic_url)).props(
                    'no-caps unelevated'
                ).classes('eeg-back-button')

def asset_url(filename: str) -> str:
    """Use the existing artwork with a version query when it is present."""
    path = ASSET_DIR / filename
    version = path.stat().st_mtime_ns if path.is_file() else 0
    return f'/assets/{quote(filename)}?v={version}'


def normalized_language(lang: str) -> str:
    language = (lang or DEFAULT_LANGUAGE).upper()
    return language if language in COPY else DEFAULT_LANGUAGE


def business_url(language: str) -> str:
    return f'/?lang={language}#business-solutions'


def setup_page(title: str, is_dark: bool):
    ui.page_title(title)
    ui.colors(primary='#0c68cf')
    ui.add_css(CSS)
    ui.add_css(SOLUTION_CSS)
    ui.add_css(SHOWCASE_CSS)
    return ui.dark_mode(is_dark)


def site_header(language: str, dark_mode, *, path: str = '/', selected_nav: int = 0) -> None:
    """Shared branding, working home/back navigation and persistent theme and language."""
    t = COPY[language]
    with ui.element('header').classes('site-header'):
        with ui.element('div').classes('header-inner'):
            with ui.element('div').classes('brand'):
                ui.label('JG').classes('brand-mark')
                ui.element('span').classes('brand-divider')
                ui.label('Julien Gouraud').classes('brand-name')

            with ui.element('nav').classes('nav-links'):
                for index, (icon, label) in enumerate(zip(NAV_ICONS, t['nav'])):
                    destination = (f'/?lang={language}' if index == 0 else
                                   business_url(language) if index == 1 else
                                   f'/?lang={language}#academic-projects' if index == 2 else
                                   f'/?lang={language}#research-papers' if index == 3 else '')
                    # Other portfolio sections are unchanged placeholders.
                    kwargs = ({'on_click': lambda to=destination: ui.navigate.to(to)}
                              if destination else {})
                    ui.button(label, icon=icon, color=None, **kwargs).props('flat no-caps').classes(
                        'nav-link' + (' active' if index == selected_nav else '')
                    )

            with ui.element('div').classes('header-controls'):
                with ui.element('div').classes('language-switch').props('role=group aria-label=Language'):
                    for lang in ('EN', 'FR'):
                        ui.button(lang, on_click=lambda choice=lang: ui.navigate.to(
                            f'{path}?lang={choice}'
                        ), color=None).props(
                            f'flat no-caps aria-pressed={str(language == lang).lower()}'
                        ).classes('lang-button' + (' selected' if language == lang else ''))

                def toggle_theme() -> None:
                    dark_mode.toggle()
                    theme = 'dark' if dark_mode.value else 'light'
                    ui.run_javascript(
                        f'document.cookie = "portfolio_theme={theme}; Path=/; Max-Age=31536000; SameSite=Lax"'
                    )
                    label = t['light_theme' if dark_mode.value else 'dark_theme']
                    theme_button.props(
                        f'aria-pressed={str(dark_mode.value).lower()} aria-label="{label}" title="{label}"'
                    )

                theme_label = t['light_theme' if dark_mode.value else 'dark_theme']
                theme_button = ui.button(on_click=toggle_theme, color=None).props(
                    f'flat round aria-pressed={str(dark_mode.value).lower()} '
                    f'aria-label="{theme_label}" title="{theme_label}"'
                ).classes('theme-toggle').bind_icon_from(
                    dark_mode, 'value', backward=lambda dark: 'light_mode' if dark else 'dark_mode'
                )


def section_header(title: str, show_all: str, accessible_label: str, row_key: str) -> None:
    """Section headings stay visible when the other rows are folded away."""
    with ui.element('div').classes('section-header'):
        ui.html(title, tag='h2').classes('section-title')
        with ui.link(show_all, target=f'#{row_key}').classes('show-all').props(
            f'aria-label="{accessible_label}" aria-expanded="false" '
            f'data-showcase-toggle="{row_key}"'
        ):
            ui.icon('arrow_forward').props('aria-hidden=true')


def demo_card(title: str, description: str, illustration: str, alt: str,
              destination: str = '') -> None:
    """Business card with a compact banner that expands on hover/focus."""
    source = asset_url(illustration)
    with ui.card().props(
        f'flat tabindex=0 role=group aria-label="{title}: {description}"'
    ).classes('demo-card showcase-card' + (' demo-card-clickable' if destination else '')) as card:
        with ui.element('div').classes('demo-banner'):
            if (ASSET_DIR / illustration).is_file():
                ui.element('img').props(
                    f'src="{source}" alt="{alt}" width=1536 height=1024 decoding=async'
                ).classes('demo-illustration')
            else:
                with ui.element('div').classes('project-image-placeholder'):
                    ui.icon('dashboard_customize')
                    ui.label(title)
            if destination:
                with ui.link(target=destination).classes('circle-arrow demo-arrow').props(
                    f'aria-label="{title}" title="{title}"'
                ):
                    ui.icon('arrow_forward').props('aria-hidden=true')
            else:
                with ui.element('div').classes('circle-arrow demo-arrow'):
                    ui.icon('arrow_forward').props('aria-hidden=true')

    if destination:
        # Both mouse and keyboard can open the complete internal demo page.
        card.on('click', js_handler=(
            f'event => {{ if (!event.target.closest("a")) '
            f'window.location.assign("{destination}"); }}'
        ))
        card.on('keydown', js_handler=(
            f'event => {{ if ((event.key === "Enter" || event.key === " ") '
            f'&& event.target === event.currentTarget) {{ event.preventDefault(); '
            f'window.location.assign("{destination}"); }} }}'
        ))


def project_card(title: str, illustration: str, destination: str = '',
                 *, icon_name: str = 'school', fallback_label: str = '') -> None:
    """Title-only academic/research tile; illustration opens only on hover/focus."""
    with ui.card().props('flat').classes(
        'project-card showcase-card' + (' project-card-clickable' if destination else '')
    ):
        with ui.element('div').classes('project-bottom'):
            ui.label(title).classes('project-title')
            if destination:
                with ui.element('div').classes('circle-arrow'):
                    ui.icon('arrow_forward').props('aria-hidden=true')
        with ui.element('div').classes('project-image-reveal'):
            if (ASSET_DIR / illustration).is_file():
                ui.element('img').props(
                    f'src="{asset_url(illustration)}" alt="{title}" loading=lazy'
                ).classes('project-image')
            else:
                with ui.element('div').classes('project-image-placeholder'):
                    ui.icon(icon_name).props('aria-hidden=true')
                    ui.label(fallback_label or title)
        if destination:
            ui.link(target=destination).classes('project-card-overlay').props(
                f'aria-label="{title}" title="{title}"'
            )


def build_homepage(language: str, is_dark: bool = False) -> None:
    t = COPY[language]
    dark_mode = setup_page('Julien Gouraud | AI Engineer', is_dark)
    ui.add_head_html(SHOWCASE_SCRIPT)
    site_header(language, dark_mode, path='/', selected_nav=0)

    with ui.element('section').classes('hero-shell'):
        with ui.element('div').classes('hero-inner'):
            with ui.element('div').classes('hero-copy'):
                ui.label(t['eyebrow']).classes('hero-eyebrow')
                ui.html(t['pitch'], tag='h1').classes('hero-pitch')
                with ui.element('div').classes('hero-actions'):
                    for label, url, style, icon in (
                        ('LinkedIn', LINKEDIN_URL, 'linkedin-button', 'linkedin'),
                        ('GitHub', GITHUB_URL, 'github-button', 'github'),
                    ):
                        button = ui.button(color=None).props('no-caps unelevated').classes(
                            f'social-button {style}'
                        )
                        with button:
                            ui.element('img').props(
                                f'src="/assets/{icon}.svg" alt="" aria-hidden="true"'
                            ).classes('social-icon')
                            ui.label(label)
                        if url:
                            button.props(f'href="{url}" target="_blank" rel="noopener noreferrer"')

            portrait = ASSET_DIR / 'portrait.png'
            if portrait.is_file():
                ui.image('/assets/portrait.png').classes('hero-portrait').bind_source_from(
                    dark_mode, 'value',
                    backward=lambda dark: '/assets/portrait-dark.png' if dark and
                    (ASSET_DIR / 'portrait-dark.png').is_file() else '/assets/portrait.png',
                )
            else:
                with ui.element('div').classes('portrait-placeholder'):
                    ui.icon('account_circle').classes('placeholder-icon')
                    ui.label(t['portrait_placeholder']).classes('placeholder-label')

    with ui.element('main').classes('main-content').props('data-active-row="all"'):
        # 1. Business solutions: three interactive demos.
        with ui.element('section').classes('explore-section showcase-section').props(
            'id=business-solutions data-showcase-row="business"'
        ):
            section_header(t['explore'], t['show_all'], t['show_all_business'], 'business')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('demos-grid'):
                        for key, filename in DEMO_IMAGES:
                            route = DEMO_ROUTES[key]
                            destination = f'{route}?lang={language}' if route else ''
                            demo_card(t[f'{key}_title'], t[f'{key}_description'], filename,
                                      t[f'{key}_image_alt'], destination)

        # 2. Research papers: independent middle row (no academic projects).
        with ui.element('section').classes('research-section showcase-section').props(
            'id=research-papers data-showcase-row="research"'
        ):
            section_header(t['research_heading'], t['show_all'], t['show_all_research'], 'research')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('projects-grid research-grid'):
                        project_card(
                            t['research_project_title'], RESEARCH_PROJECT['banner_illustration'],
                            f'/convex-deepstack?lang={language}', icon_name='psychology',
                            fallback_label=eeg_localized(RESEARCH_PROJECT['domain'], language.lower()),
                        )

        # 3. Academic projects only, each collapsed to its title at rest.
        with ui.element('section').classes('projects-section showcase-section').props(
            'id=academic-projects data-showcase-row="academic"'
        ):
            section_header(t['featured'], t['show_all'], t['show_all_academic'], 'academic')
            with ui.element('div').classes('showcase-collapse'):
                with ui.element('div').classes('showcase-collapse-inner'):
                    with ui.element('div').classes('projects-grid'):
                        academic_icons = ('directions_car', 'monitor_heart', 'rocket_launch', 'precision_manufacturing')
                        for index, (img, title) in enumerate(zip(PROJECT_IMAGES, t['projects'])):
                            destination = (f'/eeg?lang={language}' if index == 1 else
                                           f'/ball-valve?lang={language}' if index == 3 else '')
                            project_card(title, img, destination,
                                         icon_name=academic_icons[index])


def build_solution_page(key: str, language: str, is_dark: bool = False) -> None:
    """Show project-specific information without pretending the demo is finished."""
    project_title = COPY[language][f'{key}_title']
    project_alt = COPY[language][f'{key}_image_alt']
    project_image = next(image for image_key, image in DEMO_IMAGES if image_key == key)
    t = SOLUTION_COPY[key][language]
    labels = PAGE_LABELS[language]
    path = DEMO_ROUTES[key]
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    site_header(language, dark_mode, path=path, selected_nav=1)

    with ui.element('main').classes('solution-page'):
        with ui.element('div').classes('solution-breadcrumb-row'):
            with ui.link(target=business_url(language)).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(labels['breadcrumb'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        # The original illustration is the ONLY top banner (source y=0..416).
        with ui.element('section').classes('solution-art-banner'):
            with ui.element('div').classes('solution-art-inner'):
                with ui.element('div').classes('solution-visual-crop'):
                    if (ASSET_DIR / project_image).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(project_image)}" alt="{project_alt}" '
                            'width=1536 height=1024 decoding=async'
                        ).classes('solution-visual-image')
                    else:
                        ui.label(labels['missing_art']).classes('solution-image-missing')

        with ui.element('div').classes('solution-content'):
            # The large status panel is the page's main component.
            with ui.element('section').classes('solution-status').props('role=status'):
                with ui.element('div').classes('solution-status-inner'):
                    ui.label(project_title).classes('solution-project-label')
                    ui.label(t['kicker']).classes('solution-kicker')
                    with ui.element('div').classes('solution-status-icon'):
                        ui.icon('construction').props('aria-hidden=true')
                    ui.html(labels['status_title'], tag='h1').classes('solution-status-title')
                    ui.label(labels['status_soon']).classes('solution-coming')
                    ui.label(labels['status_note']).classes('solution-status-note')
                    ui.label(t['lead']).classes('solution-status-lead')

            with ui.element('section'):
                ui.html(t['summary_title'], tag='h2').classes('solution-section-heading')
                ui.label(t['summary']).classes('solution-section-intro')

            with ui.element('section'):
                ui.html(t['steps_title'], tag='h2').classes('solution-section-heading')
                with ui.element('div').classes('solution-steps'):
                    for number, (step_title, step_copy) in enumerate(t['steps'], start=1):
                        with ui.element('div').classes('solution-step'):
                            ui.label(f'{number:02d}').classes('solution-step-number')
                            ui.label(step_title).classes('solution-step-title')
                            ui.label(step_copy).classes('solution-step-copy')

            with ui.element('aside').classes('solution-example'):
                ui.icon('insights').classes('solution-example-icon').props('aria-hidden=true')
                with ui.element('div'):
                    ui.label(t['example_title']).classes('solution-example-title')
                    ui.label(t['example']).classes('solution-example-copy')

            with ui.element('div').classes('solution-actions'):
                ui.button(labels['back'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(business_url(language))).props(
                    'no-caps unelevated'
                ).classes('solution-back')


def build_eeg_page(language: str, is_dark: bool = False) -> None:
    """EEG research detail: main-site style, language, navigation, and theme."""
    project_title = eeg_localized(EEG_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    ui.add_css(EEG_CSS)
    site_header(language, dark_mode, path='/eeg', selected_nav=2)
    render_eeg_content(language.lower(), ASSET_DIR, asset_url,
                       academic_url=f'/?lang={language}#academic-projects')



# ---------------------------------------------------------------------------
# Ball-valve predictive maintenance — academic project (CIVIL-426 report)
# ---------------------------------------------------------------------------
BALL_VALVE_PROJECT = {
    'title': {
        'en': 'Ball Valve Anomaly Detection',
        'fr': 'Détection d’anomalies des vannes sphériques',
    },
    'domain': {
        'en': 'Predictive Maintenance · Hydropower',
        'fr': 'Maintenance prédictive · Hydroélectricité',
    },
    'pitch': {
        'en': (
            'A team project using real hydropower sensor data to detect abnormal ball-valve '
            'behavior. I co-developed a CNN–LSTM autoencoder that learns healthy closure '
            'patterns, scores unusual events, and supports physically interpretable fault analysis.'
        ),
        'fr': (
            'Un projet d’équipe fondé sur des données réelles de centrales hydroélectriques '
            'pour détecter les comportements anormaux des vannes. J’ai codéveloppé un '
            'autoencodeur CNN–LSTM qui apprend les fermetures saines, évalue les anomalies '
            'et facilite l’interprétation physique des défauts.'
        ),
    },
    'skills': [
        {'en': 'Predictive Maintenance', 'fr': 'Maintenance prédictive', 'icon': 'build_circle'},
        {'en': 'Time-Series Analysis', 'fr': 'Séries temporelles', 'icon': 'show_chart'},
        {'en': 'CNN–LSTM', 'fr': 'CNN–LSTM', 'icon': 'psychology'},
        {'en': 'Unsupervised Anomaly Detection', 'fr': 'Détection non supervisée', 'icon': 'troubleshoot'},
        {'en': 'Reconstruction & Rarity Scoring', 'fr': 'Reconstruction et score de rareté', 'icon': 'analytics'},
        {'en': 'K-means Clustering', 'fr': 'Clustering K-means', 'icon': 'scatter_plot'},
        {'en': 'Fault Interpretation', 'fr': 'Interprétation des défauts', 'icon': 'fact_check'},
    ],
    'overview': {
        'en': (
            'The AXPO Hydropower Challenge examined ball valves across five generating units '
            'at the Mapragg and Sarelli power stations. The team combined two complementary '
            'approaches: pressure-based detection of abnormal valve operation times, and '
            'multivariate deep-learning analysis of valve-closing events. The goal was to '
            'surface potential maintenance issues from irregularly sampled industrial signals.'
        ),
        'fr': (
            'Le défi hydroélectrique AXPO portait sur les vannes de cinq groupes aux '
            'centrales de Mapragg et Sarelli. L’équipe a combiné deux approches : '
            'la détection des durées d’ouverture ou de fermeture inhabituelles à partir '
            'de la pression, puis l’analyse multivariée des fermetures par apprentissage '
            'profond, afin de repérer des problèmes de maintenance potentiels.'
        ),
    },
    'methodology': {
        'en': (
            'For the deep-learning task, sensor data were normalized and divided into '
            'four-minute windows centered around closing transitions. A convolutional '
            'encoder and LSTM decoder learned healthy event patterns. Reconstruction '
            'error and latent-space Mahalanobis deviation were combined into a rarity '
            'score, assessed against machine- and operating-regime-specific baselines. '
            'K-means and physics-informed rules helped interpret flagged events.'
        ),
        'fr': (
            'Pour la partie apprentissage profond, les signaux ont été normalisés puis '
            'découpés en fenêtres de quatre minutes autour des fermetures. Un encodeur '
            'convolutif et un décodeur LSTM ont appris les événements sains. L’erreur '
            'de reconstruction et la distance de Mahalanobis dans l’espace latent ont '
            'alimenté un score de rareté, comparé à des références adaptées aux machines '
            'et aux régimes d’exploitation. K-means et des règles physiques ont aidé '
            'à interpréter les événements détectés.'
        ),
    },
    'contribution': {
        'en': (
            'Co-designed and implemented the CNN–LSTM autoencoder for anomaly detection, '
            'including its training strategy and anomaly-scoring framework (Task 2). '
            'The report credits this work jointly to Julien Gouraud and Loïc Sansonnens.'
        ),
        'fr': (
            'Conception et implémentation conjointes de l’autoencodeur CNN–LSTM '
            'pour la détection d’anomalies, y compris la stratégie d’entraînement '
            'et le mécanisme de score (tâche 2). Le rapport attribue ce travail '
            'à Julien Gouraud et Loïc Sansonnens.'
        ),
    },
    'key_result': {
        'value': '3',
        'caption': {
            'en': 'interpretable macro-groups emerged in the real test-set anomalies: multi-sensor inconsistencies, single-sensor drift, and coherent process deviations.',
            'fr': 'grands groupes interprétables ont émergé dans les anomalies du test réel : incohérences multi-capteurs, dérive d’un capteur et écarts cohérents du procédé.',
        },
        'secondary': {
            'en': '5 machines · 2 hydropower stations',
            'fr': '5 machines · 2 centrales hydroélectriques',
        },
    },
    'banner_illustration': 'ball-valve-anomaly.svg',
    'figure_file': 'ball-valve-test-results.png',
    'report_url': '/assets/CIVIL426_Final_Project_Report.pdf',
}

BALL_VALVE_TEXT = {
    'en': {
        'academic': 'Academic Projects', 'academic_label': 'Academic project',
        'report': 'Read project report', 'skills': 'Skills Demonstrated',
        'overview': 'Project Overview', 'methodology': 'Methodology',
        'contribution': 'My Contribution', 'result': 'Key Findings',
        'figure': 'Test-set clustering and fault-class distribution · report Figures 10–11 (p. 15)',
        'missing_report': 'Add CIVIL426_Final_Project_Report.pdf to assets/ to enable the report link.',
    },
    'fr': {
        'academic': 'Projets académiques', 'academic_label': 'Projet académique',
        'report': 'Lire le rapport', 'skills': 'Compétences mobilisées',
        'overview': 'Présentation du projet', 'methodology': 'Méthodologie',
        'contribution': 'Ma contribution', 'result': 'Principaux résultats',
        'figure': 'Clustering et types de défauts du test · figures 10–11 du rapport (p. 15)',
        'missing_report': 'Ajoutez CIVIL426_Final_Project_Report.pdf dans assets/ pour activer le lien.',
    },
}


def render_ball_valve_content(lang: str, academic_url: str) -> None:
    """Render the ball-valve project using the same components as the EEG page."""
    t = BALL_VALVE_TEXT[lang]
    project = BALL_VALVE_PROJECT
    project_title = eeg_localized(project['title'], lang)

    with ui.element('main').classes('eeg-page ball-valve-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=academic_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(t['academic'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(project_title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['academic_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(eeg_localized(project['domain'], lang))
                    ui.html(project_title, tag='h1').classes('eeg-title')
                    ui.label(eeg_localized(project['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        if (ASSET_DIR / 'CIVIL426_Final_Project_Report.pdf').is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(project['report_url'], new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label(t['missing_report']).classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner = project['banner_illustration']
                    if (ASSET_DIR / banner).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(banner)}" alt="Hydropower ball valve and sensor anomaly illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('precision_manufacturing').classes('eeg-visual-icon')
                            ui.label('HYDROPOWER  ·  AI').classes('eeg-visual-caption')

        with ui.element('div').classes('eeg-container eeg-content'):
            with ui.element('section').classes('eeg-panel eeg-skills-panel'):
                with ui.element('div').classes('eeg-section-header'):
                    ui.html(t['skills'], tag='h2').classes('eeg-section-heading')
                    ui.element('span').classes('eeg-section-rule')
                with ui.element('div').classes('eeg-skill-tags'):
                    for skill in project['skills']:
                        with ui.element('div').classes('eeg-skill-tag'):
                            ui.icon(skill['icon']).props('aria-hidden=true')
                            ui.label(eeg_localized(skill, lang))

            with ui.element('div').classes('eeg-details'):
                for key, icon in (('overview', 'device_hub'), ('methodology', 'timeline')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(eeg_localized(project[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('groups').props('aria-hidden=true')
                        ui.html(t['contribution'], tag='h2').classes('eeg-card-title')
                    ui.label(eeg_localized(project['contribution'], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('insights').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(project['key_result']['value']).classes('eeg-result-value')
                            ui.label(eeg_localized(project['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(eeg_localized(project['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure = project['figure_file']
                            if (ASSET_DIR / figure).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure)}" alt="Test-set fault clustering and distribution across fault classes" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(t['figure']).classes('eeg-figure-caption')
                            else:
                                # Never invent a benchmark when the sourced figure is absent.
                                ui.label(t['figure']).classes('eeg-figure-caption')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(t['academic'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(academic_url)) \
                    .props('no-caps unelevated').classes('eeg-back-button')


def build_ball_valve_page(language: str, is_dark: bool = False) -> None:
    """CIVIL-426 detail, embedded in the main NiceGUI site and its shared theme."""
    project_title = eeg_localized(BALL_VALVE_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    ui.add_css(EEG_CSS)
    site_header(language, dark_mode, path='/ball-valve', selected_nav=2)
    render_ball_valve_content(language.lower(), academic_url=f'/?lang={language}#academic-projects')




def render_research_content(lang: str, research_url: str) -> None:
    """Render Convex DeepStack with the same components as the academic detail pages."""
    t = RESEARCH_TEXT[lang]
    project = RESEARCH_PROJECT
    title = eeg_localized(project['title'], lang)

    with ui.element('main').classes('eeg-page research-detail-page'):
        with ui.element('div').classes('solution-breadcrumb-row eeg-breadcrumb'):
            with ui.link(target=research_url).classes('solution-breadcrumb-link'):
                ui.icon('arrow_back', size='17px').props('aria-hidden=true')
                ui.label(t['research'])
            ui.icon('chevron_right', size='15px').classes('solution-breadcrumb-chevron').props('aria-hidden=true')
            ui.label(title)

        with ui.element('section').classes('eeg-hero-section'):
            with ui.element('div').classes('eeg-container eeg-hero-inner'):
                with ui.element('div').classes('eeg-hero-copy'):
                    with ui.element('div').classes('eeg-eyebrow'):
                        ui.label(t['research_label'])
                        ui.label('•').classes('eeg-eyebrow-divider')
                        ui.label(eeg_localized(project['domain'], lang))
                    ui.html(title, tag='h1').classes('eeg-title')
                    ui.label(eeg_localized(project['pitch'], lang)).classes('eeg-pitch')
                    with ui.element('div').classes('eeg-actions'):
                        report = project['report_url']
                        if (ASSET_DIR / report.rsplit('/', 1)[-1]).is_file():
                            ui.button(t['report'], icon='open_in_new', color=None,
                                      on_click=lambda: ui.navigate.to(report, new_tab=True)) \
                                .props('no-caps unelevated').classes('eeg-report-button')
                        else:
                            ui.label('Article PDF à ajouter au dossier assets/.' if lang == 'fr'
                                     else 'Paper PDF will be linked once added to assets/.').classes('eeg-report-note')

                with ui.element('div').classes('eeg-hero-visual'):
                    banner = project['banner_illustration']
                    if (ASSET_DIR / banner).is_file():
                        ui.element('img').props(
                            f'src="{asset_url(banner)}" alt="Convex DeepStack research illustration" loading=lazy'
                        ).classes('eeg-hero-image')
                    else:
                        with ui.element('div').classes('eeg-visual-fallback'):
                            ui.icon('psychology').classes('eeg-visual-icon')
                            ui.label('CONVEX DEEPSTACK').classes('eeg-visual-caption')

        with ui.element('div').classes('eeg-container eeg-content'):
            with ui.element('section').classes('eeg-panel eeg-skills-panel'):
                with ui.element('div').classes('eeg-section-header'):
                    ui.html(t['skills'], tag='h2').classes('eeg-section-heading')
                    ui.element('span').classes('eeg-section-rule')
                with ui.element('div').classes('eeg-skill-tags'):
                    for skill in project['skills']:
                        with ui.element('div').classes('eeg-skill-tag'):
                            ui.icon(skill['icon']).props('aria-hidden=true')
                            ui.label(eeg_localized(skill, lang))

            with ui.element('div').classes('eeg-details'):
                for key, icon_name in (('overview', 'device_hub'), ('methodology', 'gps_fixed')):
                    with ui.element('article').classes('eeg-panel eeg-detail-card'):
                        with ui.element('div').classes('eeg-card-heading'):
                            with ui.element('div').classes('eeg-card-icon'):
                                ui.icon(icon_name).props('aria-hidden=true')
                            ui.html(t[key], tag='h2').classes('eeg-card-title')
                        ui.label(eeg_localized(project[key], lang)).classes('eeg-card-copy')

                with ui.element('article').classes('eeg-panel eeg-detail-card eeg-result-card'):
                    with ui.element('div').classes('eeg-card-heading'):
                        with ui.element('div').classes('eeg-card-icon'):
                            ui.icon('table_chart').props('aria-hidden=true')
                        ui.html(t['result'], tag='h2').classes('eeg-card-title')
                    with ui.element('div').classes('eeg-result-layout'):
                        with ui.element('div'):
                            ui.label(project['key_result']['value']).classes('eeg-result-value')
                            ui.label(eeg_localized(project['key_result']['caption'], lang)).classes('eeg-result-caption')
                            with ui.element('div').classes('eeg-result-pill'):
                                ui.icon('check').props('aria-hidden=true')
                                ui.label(eeg_localized(project['key_result']['secondary'], lang))
                        with ui.element('div').classes('eeg-figure-side'):
                            figure = project['figure']['file']
                            if (ASSET_DIR / figure).is_file():
                                ui.element('img').props(
                                    f'src="{asset_url(figure)}" alt="Prediction error versus search time" loading=lazy'
                                ).classes('eeg-result-figure')
                                ui.label(eeg_localized(project['figure']['caption'], lang)).classes('eeg-figure-caption')
                            else:
                                with ui.element('div').classes('eeg-visual-fallback research-figure-fallback'):
                                    ui.icon('insights').classes('eeg-visual-icon')
                                    ui.label(eeg_localized(project['figure']['caption'], lang)).classes('eeg-figure-caption')

            with ui.element('div').classes('eeg-back-row'):
                ui.button(t['research'], icon='arrow_back', color=None,
                          on_click=lambda: ui.navigate.to(research_url)).props(
                    'no-caps unelevated'
                ).classes('eeg-back-button')


def build_research_page(language: str, is_dark: bool = False) -> None:
    project_title = eeg_localized(RESEARCH_PROJECT['title'], language.lower())
    dark_mode = setup_page(f'{project_title} | Julien Gouraud', is_dark)
    ui.add_css(EEG_CSS)
    site_header(language, dark_mode, path='/convex-deepstack', selected_nav=3)
    render_research_content(language.lower(), research_url=f'/?lang={language}#research-papers')


@ui.page('/convex-deepstack')
def convex_deepstack_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_research_page(normalized_language(lang),
                        is_dark=request.cookies.get('portfolio_theme') == 'dark')


@ui.page('/ball-valve')
def ball_valve_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_ball_valve_page(normalized_language(lang),
                          is_dark=request.cookies.get('portfolio_theme') == 'dark')

@ui.page('/eeg')
def eeg_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_eeg_page(normalized_language(lang),
                   is_dark=request.cookies.get('portfolio_theme') == 'dark')


@ui.page('/')
def index(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_homepage(normalized_language(lang), is_dark=request.cookies.get('portfolio_theme') == 'dark')


@ui.page('/flowdesk')
def flowdesk_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_solution_page('flowdesk', normalized_language(lang),
                        is_dark=request.cookies.get('portfolio_theme') == 'dark')


@ui.page('/procurematch')
def procurematch_page(request: Request, lang: str = DEFAULT_LANGUAGE) -> None:
    build_solution_page('procurematch', normalized_language(lang),
                        is_dark=request.cookies.get('portfolio_theme') == 'dark')


if __name__ in {'__main__', '__mp_main__'}:
    favicon = ASSET_DIR / 'favicon.svg'
    ui.run(title='Julien Gouraud | Portfolio', favicon=favicon if favicon.is_file() else None,
           port=8080, reload=False)
