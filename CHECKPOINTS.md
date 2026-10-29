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
  - [~] Loop run from the owner account on 2026-10-22: issues #3–#7 → labels (#6 `needs-source`) → PR #8 merged. Still to do: repeat from a second account (deferred by the owner).

## Phase 3: Content layers → v0.3

- [x] **Session 9: Show content on the map** — 2026-10-22 (started with Session 8's second-account test deferred, by the owner's choice)
  - Result: `pipeline/build.py` merges `data/entries/` into `site/data/entries.json` (called by `build_site.py`). Each snapshot stands for a period up to the next snapshot; people, dynasties and cultures show while they lived or lasted, works and inventions without an end year in the period they appeared; disputed records in every period any of their claims reaches. One marker per place (Athens groups Socrates + Aristotle), colour by category (validated 8-slot palette), legend in the top-right is also the category toggle with per-period counts. Popup: dates, place, summary, Wikipedia, Sources, "Suggest an edit" (pre-filled correction form). At 500 BCE: Laozi, the Buddha, Confucius, Socrates, Aristotle, Olmecs, Maya. Checked at desktop and phone width.
- [x] **Session 10: Side panel and info cards** — 2026-10-28
  - Result: right-hand panel (replaces the legend) lists the period's entries by category, with the category toggles and counts. Clicking a list item or a marker centres the map and opens a card: dates, place, summary, disputed claims, Wikipedia, sources, GitHub record link, "Suggest an edit". Back button or Escape returns to the list; the marker gets a dark ring. On phones the panel is a bottom sheet. Checked in the browser at desktop and phone width; `validate.py` not run locally (jsonschema missing), left to the PR check.
- [x] **Session 11: Wikidata import (philosophers)** — 2026-10-28
  - Result: `pipeline/import_wikidata.py` imports philosophers whose thought is studied: Stanford / Internet Encyclopedia of Philosophy article and ≥ 50 sitelinks, plus a curated list per tradition (`pipeline/philosophers_canon.json`, 212 people in 12 traditions). 414 new records (450 in total), 41% from outside Europe (first ≥ 80-sitelink version: 22%, with Macron and Houdini and without Mencius). Dates are read from the entity data because the query service shifts BCE years by one and converts Julian dates; Socrates and Confucius are checked before writing. Existing records never overwritten. Template summaries from CC0 descriptions. `validate.py` 0 problems; re-running writes nothing; checked in the browser. Details, spread and the 16 skipped in `docs/data-notes.md`.
- [x] **Session 12: More categories** — scientists, writers, works — 2026-10-28
  - Result: `import_wikidata.py` now takes `--category` (philosopher, scientist, writer, work; default all). Scientists: MacTutor biography + ≥ 80 sitelinks, plus `scientists_canon.json`; writers and works: curated lists only (`writers_canon.json`, `works_canon.json`), named by English Wikipedia article title and resolved to Wikidata items. Works are dated by publication/inception (else the author's floruit, circa) and placed with their author unless the list gives a place. 1,005 new records (1,455 in total): 355 scientists, 428 writers, 222 works. `validate.py` 0 problems; re-running writes nothing; `build_site.py` runs. Not checked in the browser (navigation was denied). Inventions stay curated/community-only. Details in `docs/data-notes.md`.
- [x] **Session 13: Data-quality report** — `docs/data-quality.md`, flags not deletions — 2026-10-28
  - Result: `pipeline/quality_report.py` reads `data/entries/` and writes `docs/data-quality.md` (deterministic; changes no record). Checks: possible duplicates (same name+category, or same birth year with nested names), coordinates (0,0, or a place name far from where other records put it), low-precision dates (114 century/decade/circa, share per category), outliers (lifespan > 105, person without end year, work spanning > 100 years, short summary, single source, no Wikipedia link). On 1,455 records: 0 duplicates, 6 coordinate flags (mostly same-name places such as Cambridge UK/US, to be judged by a human), 12 outliers. Opening issues labelled `good first issue` is not done; the report lists the to-dos.
- [x] **Session 14: Automatic build and deploy** — on merge: validate → build → Pages — 2026-10-28
  - Result: `.github/workflows/pages.yml` now has two jobs: `validate` (`pipeline/validate.py`) and `deploy` (`needs: validate`; `build_site.py`, then upload and deploy to Pages). A failing record blocks publishing. Checked locally only; the first run on `main` after merge is the real test.

## Phase 4: Polities, rulers and dynasties → v0.4

- [x] **Session 15: Click a state, learn what it is** — `data/polities/` — 2026-10-28
  - Result: 86 polity records (`data/polities/`, schema `pipeline/polity.schema.json`, seeded by `pipeline/make_polities.py` from `polities_seed.json`; Wikidata ids looked up from Wikipedia titles). `validate.py` checks them (border names must exist in a snapshot, no two states claim a name at overlapping dates; broken record tested: fails). `build.py` writes `site/data/polities.json`. Clicking a realm opens its card in the side panel (dates, capital, summary, sources, suggest-an-edit and border-error links); unmatched land keeps the old popup. Checked in the browser at desktop and phone width: Achaemenid Empire at 500 BCE, Egypt/Persia picked by era, no console errors.
- [x] **Session 16: Rulers and dynasties** — 2026-10-29
  - Result: new record types `data/dynasties/` and `data/rulers/` (schemas `pipeline/dynasty.schema.json`, `ruler.schema.json`; `validate.py` checks polity/dynasty links and reign dates). 17 curated states (Achaemenid, Parthian, Sasanian, Egypt, Han, Rome, Byzantium, Abbasid, Mongol, Tang, Ming, Qing, Ottoman, England, France, Russia, Inca): 209 records via `pipeline/rulers_seed.py` → `make_rulers.py`. `build.py` writes `site/data/rulers.json`; state cards list dynasties and rulers and mark who is in power at the slider's year (Achaemenid at 500 BCE → Darius the Great; no console errors). Deviation from the roadmap: no bulk Wikidata import — a coverage check found reign data too thin (e.g. 9 Achaemenid monarchs, none for Aksum or Kush). Reign years are from memory of the Wikipedia articles and unreviewed; a few differ from Wikidata by 1–6 years.
- [x] **Session 17: Timeline strip** — 2026-10-29
  - Result: opening a state card shows an SVG strip under the map (`#timeline` in `site/index.html`): dynasties as bars (overlaps stack in rows), rulers as a row of ticks, a red marker at the slider's year labelled with who is in power. It follows the slider, hides when the card closes or the state has no ruler data, and clicking a bar jumps to the nearest snapshot. Checked in the browser: Achaemenid at 500 BCE → Darius the Great; Han (2 dynasties); phone width has no horizontal overflow; no console errors; `validate.py` passes. Note: the card's reign highlights still use the year the state was clicked, while the strip follows the slider.

## Phase 5: Follow a country through time → v0.5

- [x] **Session 18: Spatial lineage** — geopandas, equal-area (EPSG:6933), one snapshot at a time — 2026-10-29
  - Result: `pipeline/download_countries.py` (Natural Earth 110m, pinned) and `pipeline/make_lineage.py` write `data/lineage/<ADM0_A3>.json` for 176 countries × 14 snapshots (+ `index.json`), automatic and marked so. Iran at 500 BCE → Achaemenid Empire 99 %; Egypt 1914 → Egypt under the UK 98 %. `validate.py` checks the files; `build_site.py` copies them to `site/data/lineage/`. Method and limits in `docs/data-notes.md`. No UI yet (Session 19).
- [x] **Session 19: "Follow a country" mode** — 2026-10-29
  - Result: `build_site.py` writes `site/data/countries.json` (176 outlines, 156 KB; the Pages workflow now downloads the Natural Earth file first). The side panel has a "Follow a country" selector: the country's outline stays on the map through all snapshots and the panel lists who held it at the slider's snapshot with shares; named states open their polity card. Egypt at 1914 → Egypt 98 %; Egypt at 500 BCE → Saharan pastoral nomads 45 %, Achaemenid Empire 44 %; Stop clears it; no console errors; `validate.py` passes. Not checked at phone width or visually (checked by script). 110m outlines: small countries and islands are missing. Automatic data, marked as approximate in the panel.
- [x] **Session 20: Curated lineages** — ~10 countries, sourced — 2026-10-29
  - Result: `data/lineage_curated/` holds 10 curated files (Egypt, Iran, Iraq, Turkey, Greece, Italy, France, Spain, China, India), made by `pipeline/make_curated_lineage.py` from `curated_lineage_seed.json`: noise and slivers dropped, per-snapshot notes and source links added; shares stay those of the automatic area match. France drops French Guiana (the old "Manioc farmers" entry) and is rescaled to mainland. `validate.py` checks curated files (source URLs, state names must exist in the snapshot; a broken name fails). `build_site.py` overlays them and marks them in the index; the panel shows ★ in the selector, notes and a Sources list, other countries keep the "automatic" caveat. Checked in the browser (France at 400 → Western Roman Empire 100 %); phone width not checked. Notes and sources are from memory and unreviewed.
- [x] **Session 21: Measuring border change** — area-over-time chart — 2026-10-29
  - Result: `pipeline/make_areas.py` writes `data/areas/areas.json` (86 polities: recorded and carried-forward km², gained/lost since the previous snapshot; deterministic). `validate.py` checks it, `build_site.py` copies it. State cards have a "Territory over time" chart (points clickable, red at the slider snapshot) and the change numbers. Roman Empire: 4.25 M km² in 1 BCE, split at 400 CE (only 2 snapshots, see `docs/data-notes.md`). Checked in the browser, no console errors; phone width not checked; no map overlay of gained/lost land.

## Phase 6: Environment (could have) → v0.6

- [x] **Session 22: Research and decide** — `docs/environment-decision.md` — 2026-10-29
  - Result: `docs/environment-decision.md` written. HYDE 3.5 (10,000 BCE–2025, 5 arc-minute) chosen as the one source; plan is a single cropland overlay labelled "model estimate"; no climate layer, no per-pixel values, no causation claims. **Open:** HYDE's license and exact time steps could not be read (landing page blocked bots), so Session 23 starts by checking them in a normal browser; if the terms don't allow derived images, skip to Session 24. Docs only; nothing run.
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
