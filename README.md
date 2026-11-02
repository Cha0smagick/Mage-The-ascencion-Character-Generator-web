# Mage: The Ascension — Character Sheet Generator

The ultimate tool for creating *Mage: The Ascension* character sheets, faithful to the lore, for any character of any Tradition, Convention, Craft, or alignment. Fully printable (A4) and deployable to GitHub Pages via GitHub Actions.

## Languages
- **Primary:** English
- **Secondary:** Spanish (inline labels marked with `.es`)

## What it does
- Generates a complete Mage character: Nature, Demeanor, Paradigm, Morality, Affiliation (Tradition / Convention / Craft / Other), Sphere affinity, Concept, Background, Goal, Secret, Merits & Flaws, Cherished Possession, and Appearance.
- Attributes (7/5/3), Abilities (Talents 13 / Skills 9 / Knowledges 5), Backgrounds (5 points), Spheres (affinity = 1 + 5 points, max 3 at creation).
- Willpower, Paradox, and Health trackers with printable boxes.
- Two-page sheet: Page 1 = stats; Page 2 = story & notes.
- **Lock** any section and re-roll the rest.
- Export to **PDF** (browser "Save as PDF" via Print) and **Print** directly.

## Project structure
```
index.html        # Single-page static app (no server required)
style.css         # Mage aesthetic: dark parchment, Cinzel/Uncial Antiqua/Lora fonts, hermetic seal, print styles
data.js           # Lore data (spheres, Traditions, Conventions, lists) — EN primary / ES secondary
app.js            # Generation logic + rendering + print export (dependency-free)
.github/workflows/deploy.yml   # GitHub Actions -> GitHub Pages
AUDITORIA_EXISTENTE.md         # Audit of the previous Streamlit prototype (why it was replaced)
```

## How to run locally
Open `index.html` in any modern browser. No build step, no dependencies, no API keys.

## Deploy to GitHub Pages
1. Push this repo to GitHub (branch `main`).
2. Enable GitHub Pages in repo Settings → Pages → Build from `gh-pages` (the workflow handles deployment).
3. On every push to `main`, the GitHub Actions workflow builds and deploys the static site automatically.

## Print / PDF
- Click **Print Sheet** → browser print dialog → choose "Save as PDF" (A4, margins none) for a print-ready character sheet.
- Print styles strip UI controls and use vector-friendly layout.

## Lore fidelity
- Nine Spheres with correct Tradition/Convention affinities (Order of Hermes → Forces, Virtual Adepts → Correspondence, Sons of Ether → Matter, etc.).
- Technocracy Conventions (Progenitors, Void Engineers, Syndicate, NWO, Iteration X).
- Crafts and other factions (Hollow Ones, Marauders, Nephandi, Solitary Awakened).
- No Vampire/Changeling cross-contamination.

## Notes / known limits
- Portrait generation is intentionally omitted: the previous prototype relied on an unreliable external image service (`freeGPTFix`/pollinations). Add your own portrait by pasting an image into the sheet before printing if desired.
- Character data lives only in the browser session (no backend/database). Save/export via Print to PDF.

## Audit of prior code
See `AUDITORIA_EXISTENTE.md` — the previous Streamlit app was not deployable to GitHub Pages, had incomplete point-buy logic, mixed English/Spanish data, and contaminated lore (Vampire/Changeling factions). It was replaced by this static, dependency-free, print-ready generator.
