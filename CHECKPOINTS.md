# Checkpoints

One line per roadmap session ([docs/roadmap.md](docs/roadmap.md)). A session is ticked only
when its **Result** exists and has been checked. Rule from the roadmap: don't start a new
session with the previous one half-done.

Legend: `[x]` done · `[~]` partly done (see note) · `[ ]` not started

## Phase 0: Setup

- [x] **Session 0: Workspace and repository** — 2026-10-19
  - [x] Folder structure (`data/entries`, `data/polities`, `data/borders`, `pipeline`, `site`, `docs`, `.github`, `raw`) — 2026-10-19
  - [x] `.gitignore` ignores `raw/` and `site/data/` — 2026-10-19
  - [x] `README.md`, roadmap copied to `docs/roadmap.md` — 2026-10-19
  - [x] Install Git, VS Code, Node.js LTS — already installed (Git 2.55, Node 24.12, Python 3.14, gh 2.101) — 2026-10-19
  - [x] `git init` (branch `main`), `.gitattributes` for LF line endings, first commit — 2026-10-19
  - [x] Public GitHub repo created and `main` pushed: https://github.com/omidhey/world-history-map — 2026-10-19

## Phase 1: MVP map with a time slider → v0.1

- [x] **Session 1: One map on screen** — 2026-10-19
  - Result: `site/index.html` draws `world_1500.geojson` (291 polygons) with Leaflet 1.9.4 (bundled locally, no CDN). Run with `run_site.bat`.
- [x] **Session 2: Download and shrink the snapshots** — 2026-10-19
  - Result: `pipeline/download_borders.py` (upstream pinned to `da7a4b7`, mapshaper 0.7.90 via `npm install`) writes 14 files to `data/borders/` (133–601 KB each, 4.2 MB total) plus `manifest.json`. Sizes in `docs/data-notes.md`.
  - Fix (2026-10-19): realms vanishing between snapshots investigated with `pipeline/gap_report.py`. The pipeline no longer loses features or islands (explode before simplifying, no coordinate rounding), and 8 sourced corrections are in `data/borders/overrides.json` (purple outline on the map). See `docs/vanished-realms.md`.
  - Rule (2026-10-19): coloured land never goes back to uncoloured; `pipeline/carry_forward.py` keeps the last recorded realm, shown pale with a "last recorded" tooltip.
- [x] **Session 3: The time slider** — 2026-10-19
  - Result: slider + ‹ › buttons + arrow keys + clickable year ticks, driven by the manifest. Loaded files are cached, neighbours prefetched, stale loads ignored. `pipeline/build_site.py` copies `data/borders/` into `site/data/`.
- [x] **Session 4: Make it readable** — 2026-10-19
  - Result: FNV-1a hash of `SUBJECTO` → stable colour; hover shows `NAME` (+ "under …"), highlighted outline; `BORDERPRECISION` 1 dashed and faded; unnamed land neutral. Checked in browser at desktop and phone width.
- [x] **Session 5: Publish v0.1** — 2026-10-19 → **MVP live**: https://omidhey.github.io/world-history-map/
  - [x] Credits footer (historical-basemaps, GPL-3.0, "borders are approximate"), `.github/workflows/pages.yml` — 2026-10-19
  - [x] Pushed, Pages enabled (source: GitHub Actions), deploy run succeeded, live page checked (slider 3000 BCE–2010, no console errors) — 2026-10-19

## Phase 2: Open-source and contribution foundation → v0.2

- [x] **Session 6: Project rules** — 2026-10-22
  - Result: `LICENSE` (GPL-3.0, code + borders), `LICENSE-TEXT.md` (CC BY-SA 4.0 for contributed text, CC0 Wikidata facts), `CONTRIBUTING.md` (incl. licensing grant), `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1, contact semifact@gmail.com), one-page `docs/content-policy.md`; README Licensing + Contributing sections; licence link in the site footer.
- [x] **Session 7: Schema, validator and automatic checks** — 2026-10-22
  - Result: `pipeline/entry.schema.json` + `pipeline/validate.py` (jsonschema 4.25.1; no year 0, start ≤ end, id = file name, no duplicate ids / Wikidata ids, disputed ⇒ claims, overrides sourced), `docs/schema.md`, 33 records in `data/entries/` (all 8 categories, 3200 BCE–1934 CE, QIDs and dates checked against Wikidata, 5 disputed). `.github/workflows/validate.yml`; `main` protected with required check `validate` (admins may bypass). Test PR #2 with year 0: red and merge blocked, fixed → green, closed.
- [~] **Session 8: Contribution path for non-programmers** — issue forms, "Suggest an edit" links, review labels, PR template → **contributions with admin approval**
  - [x] Issue forms (add / correct / border error, source required, auto-label `needs-review`), `config.yml`, PR template, labels `needs-review` `accepted` `needs-source` `rejected`, review flow in `CONTRIBUTING.md` — 2026-10-22
  - [x] Site: `suggestEditUrl()` helper; clicking a realm opens a popup with a pre-filled "Report a border error" link; footer "Suggest an addition" — 2026-10-22
  - [ ] Full loop with a second account: suggestion → review → merged PR → live (needs Phase 2 PR merged first)

## Phase 3: Content layers → v0.3

- [ ] **Session 9: Show content on the map** — `pipeline/build.py`, markers by period, category toggles
- [ ] **Session 10: Side panel and info cards**
- [ ] **Session 11: Wikidata import (philosophers)** — check BCE years against known dates
- [ ] **Session 12: More categories** — scientists, writers, works
- [ ] **Session 13: Data-quality report** — `docs/data-quality.md`, flags not deletions
- [ ] **Session 14: Automatic build and deploy** — on merge: validate → build → Pages

## Phase 4: Polities, rulers and dynasties → v0.4

- [ ] **Session 15: Click a state, learn what it is** — `data/polities/`
- [ ] **Session 16: Rulers and dynasties**
- [ ] **Session 17: Timeline strip**

## Phase 5: Follow a country through time → v0.5

- [ ] **Session 18: Spatial lineage** — geopandas, equal-area (EPSG:6933), one snapshot at a time
- [ ] **Session 19: "Follow a country" mode**
- [ ] **Session 20: Curated lineages** — ~10 countries, sourced
- [ ] **Session 21: Measuring border change** — area-over-time chart

## Phase 6: Environment (could have) → v0.6

- [ ] **Session 22: Research and decide** — `docs/environment-decision.md`
- [ ] **Session 23: One overlay** — one HYDE variable as PNG overlays
- [ ] **Session 24: Environmental events**

## Phase 7: Engineering quality → v1.0

- [ ] **Session 25: Code and tests** — JS modules, pytest
- [ ] **Session 26: Performance** — TopoJSON, `docs/performance.md`
- [ ] **Session 27: Search and shareable links** — Fuse.js, URL state
- [ ] **Session 28: Release v1.0 and open data** — About page, contributors, tag, Zenodo DOI

## Phase 8: Own contribution platform (only when needed) → v2.0

- [ ] **Session 29: Design document** — `docs/platform-design.md`
- [ ] **Session 30: FastAPI read-only API + import**
- [ ] **Session 31: Login and roles**
- [ ] **Session 32: Edit form → pending submission**
- [ ] **Session 33: Moderation queue**
- [ ] **Session 34: History page and revert**
- [ ] **Session 35: Export to repo, deploy, switch "Suggest an edit"**
