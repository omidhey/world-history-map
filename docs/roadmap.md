# Interactive World History Map: Roadmap

An open-source, community-edited website that shows the world map from about 3000 BCE to today. Visitors can explore culture, literature, books, scientists, philosophers, rulers, dynasties and inventions in each period, and can follow one country's borders and environment over time. Anyone can propose additions or corrections, and an admin approves them before they go live.

**How to use this roadmap**

- Each session is sized for roughly 60–90 minutes and ends with something you can open, run or show.
- Sessions inside a phase depend on each other in order. Phases 5 and 6 can swap.
- If a session runs over, stop at its "Result" line and carry the rest into the next session. Do not start a new session with the previous one half-done.
- The site is public after **Session 5**. It accepts community contributions with admin approval from **Session 8**.

---

## 1. Key decisions

### 1.1 How contributions work: Git first, own backend later

A Wikipedia-like site needs four things: people can propose changes, an admin reviews them, every change has a history and an author, and bad changes can be reverted. You can get all four for free, with no server, by keeping the data as files in a public GitHub repository.

| Stage | Who can contribute | How the admin approves | Cost and maintenance |
|---|---|---|---|
| **A. Git as the database** (from Session 7) | Anyone with a GitHub account, by editing a data file and opening a pull request | You review the diff and merge it. An automated check rejects malformed data before you look. | Free. No server, no passwords to protect, no backups to run. |
| **B. "Suggest an edit" forms** (from Session 8) | Anyone with a GitHub account, by filling a form. No coding needed. | You review the suggestion, then apply it yourself or accept a pull request for it. | Free. Still no server. |
| **C. Own contribution platform** (Phase 8, only when needed) | Anyone with an account on your site, through edit forms on the site itself | A moderation queue on the site: view the change, approve or reject with a reason, revert from the history page | A server, a database, login handling, spam protection and backups. Low cost, but real ongoing work. |

**Why this order.** Stages A and B give you version history, attribution, revert and a review screen (the pull-request diff) for free. They also teach the workflow that real open-source projects use. Stage C is the true Wikipedia-style experience, but it means running software that strangers write into. That brings security, spam and backup responsibilities, so build it once there is real demand. Section 8.1 lists the signals that say it's time.

**Rejected for now: running MediaWiki or Wikibase** (the software behind Wikipedia and Wikidata). It is the most complete option, but it needs PHP, a database and a search service. It is heavy to host and doesn't fit a map-first site well.

### 1.2 Stack

| Part | Choice | Reason |
|---|---|---|
| Map in the browser | **Leaflet 1.9.x** | Draws GeoJSON directly, small API, many examples. Switch to MapLibre GL only if measurements in Session 26 show Leaflet is too slow. |
| Front-end | **Plain HTML + CSS + JavaScript** | A map, a slider and a panel do not need a framework yet. |
| Source data | **One JSON file per record** in `data/` | One file per person or work means two contributors rarely edit the same file. Diffs stay small and readable, and each record gets its own history. |
| Checking and building | **Python scripts**, run automatically by **GitHub Actions** (free for public repositories) | Every pull request is checked against the schema. Every merge rebuilds the site's data files and republishes. |
| Hosting | **GitHub Pages** (free) | Static files, HTTPS, deploys on merge. |
| Later backend (Stage C) | **FastAPI + PostgreSQL** (PostGIS for geometry) | Python, well documented, and Postgres runs on your 8 GB laptop for development. |

### 1.3 Data sources (checked 2026-10-19)

| Need | Source | Notes |
|---|---|---|
| Historical borders | **historical-basemaps**, `github.com/aourednik/historical-basemaps` | Verified today: 54 snapshots from 123000 BCE to 2010, including 3000 BCE. Each file is 0.8–2 MB. Fields: `NAME`, `SUBJECTO` (ruling power), `PARTOF`, `BORDERPRECISION` (1–3). Some polygons have no name. **GPL-3.0.** The author says it is work in progress. |
| People, works, rulers | **Wikidata** SPARQL endpoint | CC0 (no restrictions). I couldn't reach it from my sandbox, so the query details come from documentation; Session 11 is where you test them. |
| Modern countries | **Natural Earth** Admin-0, 1:110m | Public domain. |
| Environment (optional) | **HYDE 3.x** (PBL Netherlands): gridded population and land use | Confirm the current version and license in Session 22. |

### 1.4 Licenses (decide in Session 6, not legal advice)

An open project needs these decided before the first outside contribution. Changing them later requires permission from every contributor.

- **Code:** GPL-3.0. This matches the border data's license and avoids any compatibility questions.
- **Border data:** stays GPL-3.0 because it is derived from historical-basemaps. Keep its credit and license file.
- **Text contributed by people** (summaries, descriptions): **CC BY-SA 4.0**, the same license as Wikipedia. Copying Wikipedia text is then allowed, but only with attribution. The simpler rule is to write your own summaries and link to Wikipedia.
- **Records imported from Wikidata:** CC0, so they can be mixed in freely.
- `CONTRIBUTING.md` states that by submitting, contributors license their contribution under these terms.

### 1.5 Data conventions (fixed in Session 7)

- **Years are integers. Negative means BCE. There is no year 0.** historical-basemaps already works this way. Some sources include a year 0, which shifts every BCE date by one. Test with a known date (Socrates died 399 BCE).
- **Borders are snapshots.** The slider snaps to the latest snapshot at or before the chosen year and says "Borders as of 323 BCE". Borders are never interpolated.
- **Every record carries `sources` (at least one), `date_precision`, and a stable `id`.** No source, no merge. This is the main quality rule for the whole project.
- **Imported records belong to the repository once they are merged.** Re-running a Wikidata import adds new records and reports differences. It never silently overwrites something a contributor corrected.
- **Disputed facts are shown as disputed.** A record can hold more than one dated claim, each with its own source, plus a `disputed: true` flag. This is how the site handles contested dates and borders without the admin having to pick a winner.

---

## 2. Phase 0: Setup (1 session)

### Session 0: Workspace and repository
- Install Git, VS Code and Node.js LTS (Node only runs mapshaper). You already have Python.
- Create a **public** GitHub repository `world-history-map`:

```
world-history-map/
  data/              # source of truth, edited by contributors
    entries/         # one JSON file per person, work, invention, ruler...
    polities/        # one file per state or dynasty
    borders/         # simplified border snapshots
  pipeline/          # Python: download, validate, build
  site/              # the web page; site/data/ is generated, not edited
  docs/              # decisions, schema, data notes, this roadmap
  .github/           # issue forms, pull-request template, Actions workflows
  raw/               # downloads, git-ignored
```

- **Result:** a public repository with this structure and `raw/` and `site/data/` in `.gitignore`.

---

## 3. Phase 1: MVP map with a time slider (Sessions 1–5)

### Session 1: One map on screen
- Download `world_1500.geojson` by hand. Write `index.html` that loads Leaflet and draws it. Serve with `python -m http.server`, because browsers block local JSON loaded from `file://`.
- **Result:** the world in 1500 in your browser.

### Session 2: Download and shrink the snapshots
- `pipeline/download_borders.py` downloads 14 snapshots that cover the major changes: `-3000, -2000, -1000, -500, -323, -1, 400, 800, 1200, 1500, 1800, 1914, 1945, 2010`.
- Simplify each with `npx mapshaper <in> -simplify 10% keep-shapes -o <out>`, called from the Python script so the step can be repeated. Write `data/borders/manifest.json`.
- **Result:** 14 small files, with before and after sizes recorded in `docs/data-notes.md`. A few hundred KB per file is an estimate; confirm it by measuring.

### Session 3: The time slider
- A range input driven by the manifest. On change, load that year's file (cache files already loaded) and swap the layer. Label it "Borders as of …".
- **Result:** slide from 3000 BCE to 2010 and watch the map change.

### Session 4: Make it readable
- Color by `SUBJECTO` with a stable hash, so a state keeps its color across snapshots. Hovering shows `NAME`. Borders with `BORDERPRECISION` 1 are drawn faded or dashed.
- **Result:** a map a stranger can read.

### Session 5: Publish v0.1
- GitHub Pages, plus a footer that credits historical-basemaps and says borders are approximate.
- **Result:** a public URL. **This is the MVP.**

---

## 4. Phase 2: Open-source and contribution foundation (Sessions 6–8)

This phase comes before most content, so every record from now on enters through the same reviewed path.

### Session 6: Project rules
- `LICENSE` and a licensing section in `README.md` (section 1.4), `CONTRIBUTING.md`, a `CODE_OF_CONDUCT.md` (the Contributor Covenant is a common free template).
- `docs/content-policy.md`, one page long: sources required, neutral wording, how to mark disputed facts, what gets rejected (unsourced claims, copied text, political advocacy).
- **Result:** someone landing on the repository knows what they may contribute and how it will be judged.

### Session 7: Schema, validator and automatic checks
- Define the record format in `docs/schema.md` and as a Python check (`pydantic` or `jsonschema`):

```json
{
  "id": "socrates",
  "wikidata": "Q913",
  "name": "Socrates",
  "category": "philosopher",
  "start": -470, "end": -399,
  "date_precision": "year",
  "location": {"lat": 37.97, "lon": 23.72, "place": "Athens"},
  "summary": "Written in your own words, one or two sentences.",
  "links": {"wikipedia": "https://en.wikipedia.org/wiki/Socrates"},
  "sources": ["https://www.wikidata.org/wiki/Q913"],
  "disputed": false
}
```

  Categories: `philosopher, scientist, writer, work, invention, ruler, dynasty, culture`.
- Hand-write about 30 records across categories and periods, one file each in `data/entries/`.
- `pipeline/validate.py` fails on missing sources, year 0, start after end, duplicate IDs, or unknown categories.
- A GitHub Actions workflow runs the validator on every pull request. A pull request with a red check cannot be merged.
- **Result:** open a deliberately broken pull request and watch it fail, then fix it and watch it pass.

### Session 8: Contribution path for non-programmers
- GitHub **issue forms** in `.github/ISSUE_TEMPLATE/`: "Add a person or work", "Correct an entry", "Report a border error". Each has fields for name, dates, place and source (required).
- A **"Suggest an edit"** link on every info card in the site that opens a pre-filled issue. This uses GitHub's URL parameters, so there is no backend.
- Labels for your review flow: `needs-review`, `accepted`, `needs-source`, `rejected`.
- A pull-request template with a checklist: sources added, own words, dates checked.
- **Result:** test the full loop with a second GitHub account or a friend. They suggest something, you review it, it is merged and appears on the live site. **The site now accepts contributions with admin approval.**

---

## 5. Phase 3: Content layers (Sessions 9–14)

### Session 9: Show content on the map
- A build script (`pipeline/build.py`) merges `data/entries/*.json` into `site/data/entries.json`. The page shows entries whose lifespan overlaps the selected period as markers, with category toggles.
- **Result:** at 500 BCE you see Confucius, the Buddha (with approximate dates) and early Greek thinkers.

### Session 10: Side panel and info cards
- A list of everything visible in the period, grouped by category. Clicking an item centers the map and opens a card with dates, summary, sources, links and the "Suggest an edit" button.
- **Result:** the map is browsable, and every card invites a correction.

### Session 11: Wikidata import (philosophers)
- `pipeline/import_wikidata.py`: query humans with occupation *philosopher*, with birth and death dates, birthplace coordinates, label and sitelink count. Send a descriptive `User-Agent` and cache raw results in `raw/`.
- Check BCE years against two known dates. Filter by sitelink count so the map is not flooded.
- The script writes new record files on a branch and opens one pull request. You review it like any other contribution.
- **Result:** a few hundred philosophers, entered through the same reviewed path as human edits.

### Session 12: More categories
- Run the import for scientists, writers and literary works. Inventions are poorly structured in Wikidata, so they grow through curated records and community contributions instead.
- **Result:** every category has content.

### Session 13: Data-quality report
- A script that reports duplicates, missing coordinates, low-precision dates and outliers. It writes `docs/data-quality.md` and, optionally, opens issues labelled `good first issue` for contributors to fix.
- Fix with flags, never by deleting records.
- **Result:** a quality report, and a ready-made to-do list for new contributors.

### Session 14: Automatic build and deploy
- A second GitHub Actions workflow: on every merge to `main`, run validate, then build, then publish to GitHub Pages.
- **Result:** after you approve and merge a contribution, the live site updates without you doing anything else.

---

## 6. Phase 4: Polities, rulers and dynasties (Sessions 15–17)

### Session 15: Click a state, learn what it is
- `data/polities/` records link a border `NAME` to a Wikidata ID and a description. Start with the 50–100 most visible states; contributors can add the rest.
- **Result:** clicking "Achaemenid Empire" opens its card.

### Session 16: Rulers and dynasties
- Import what Wikidata has, then curate the top 15–20 states by hand. Coverage of ancient states is uneven.
- **Result:** state cards list rulers and dynasties with dates and sources.

### Session 17: Timeline strip
- A horizontal SVG strip under the map with the selected state's dynasties as bars and a marker at the current year.
- **Result:** you see at a glance who ruled at the slider's year.

---

## 7. Phase 5: Follow a country through time (Sessions 18–21)

Names change (the land of modern Iran was Elam, Media, the Achaemenid, Seleucid, Parthian and Sasanian Empires, and more), so matching by name fails. Matching by **area** works automatically.

### Session 18: Spatial lineage (offline, Python + geopandas)
- For each modern country and each snapshot, find which historical polygons cover it and what share of its area each covers. Compute areas in an equal-area projection (for example EPSG:6933), not in degrees. Process one snapshot at a time.
- **Result:** files such as `lineage/IRN.json` with year → [(state, area share)].

### Session 19: "Follow a country" mode
- Choose a modern country. Its outline stays on screen through all snapshots, with the list of ruling powers beside the slider.
- **Result:** pick Egypt and watch who held that land.

### Session 20: Curated lineages
- Automated results will include slivers and noise. Curated lineage files for about 10 countries override them, with sources. Contributors can add more through the same review path.
- **Result:** clean, sourced histories for 10 countries, with automated ones marked as such.

### Session 21: Measuring border change
- Area-over-time chart for any state, and an optional "gained and lost territory" view between two snapshots.
- **Result:** for example a chart of Roman territory from 500 BCE to 400 CE, generated from the data.

---

## 8. Phase 6: Environment (Sessions 22–24)

There is no single free dataset of each country's environment over 5000 years. This phase is a "could have".

- **Session 22: research and decide.** Read HYDE 3.x documentation and license, and look at one climate reconstruction. Write `docs/environment-decision.md` saying what you will show and what you won't claim.
- **Session 23: one overlay.** One HYDE variable (cropland or population), downsampled, exported as PNG overlays one year at a time to stay inside 8 GB of RAM.
- **Session 24: environmental events.** Sourced records for events such as the drying of the Sahara, the 536 CE volcanic event, the Little Ice Age and the shifting head of the Persian Gulf. They use the same schema and review path as other content.

---

## 9. Phase 7: Engineering quality and v1.0 (Sessions 25–28)

- **Session 25: code and tests.** Split the JavaScript into modules. Add `pytest` tests for validation, BCE handling and lineage shares.
- **Session 26: performance.** Measure, then convert snapshots to TopoJSON (shared borders stored once) and load only the year in view. Write before and after numbers in `docs/performance.md`.
- **Session 27: search and shareable links.** Client-side search (Fuse.js), and view state in the URL (`?year=-500&country=IRN&layers=philosopher`).
- **Session 28: release v1.0 and open data.** Mobile check, an About page with sources, licenses and limitations, a contributor list generated from git history, and a tagged release. Connect the repository to **Zenodo** (free) so every release of the dataset gets a citable DOI. That makes the data citable in research and is good evidence of your work for a portfolio.

---

## 10. Phase 8: Own contribution platform (Sessions 29–35, only when needed)

### 10.1 When to start this phase
Start when at least one of these is true, not before:
- People tell you they want to contribute but won't create a GitHub account.
- Suggestions arrive faster than you can turn issues into changes by hand.
- You want other people to share the admin work with proper roles.

Until then, Stage B costs nothing and already gives full history and review.

### 10.2 Design
- **Data model:** `records` (current approved version), `revisions` (every approved version, with author, time and comment), `submissions` (proposed changes waiting for review), `users` with roles `contributor`, `reviewer`, `admin`.
- **Rule:** nothing a user submits reaches `records` without a reviewer approving it. This is the same rule as Stage A, now enforced by the database instead of by GitHub.
- **The repository stays the public record.** Approved changes are exported back to `data/` as JSON files, so the open dataset, its history and its releases continue.
- **Protection:** login (GitHub sign-in or emailed one-time links, so you don't store passwords), rate limits, a free CAPTCHA on submission forms, and daily database backups.
- **Hosting:** a small virtual server or a free tier. Free-tier terms change often, so check them when you reach this phase. Develop locally first; Postgres and FastAPI run fine on 8 GB.

### 10.3 Sessions
- **Session 29:** design document (`docs/platform-design.md`) with tables, roles, approval flow and threat list (spam, vandalism, political edit wars).
- **Session 30:** FastAPI app with a read-only API serving records from Postgres, plus an import from `data/`.
- **Session 31:** login and roles.
- **Session 32:** "Edit" form on the site that creates a pending submission.
- **Session 33:** moderation queue page: side-by-side diff, approve, reject with a reason the contributor sees.
- **Session 34:** history page per record (who changed what and when) with one-click revert.
- **Session 35:** export approved changes to the repository, deploy, and switch the "Suggest an edit" button to the new form.

**Border editing by the public stays out of scope even here.** Editing polygons in a browser is hard to do well and easy to abuse. Border corrections continue as GeoJSON files in pull requests, checked automatically for valid geometry and reviewed by an admin in QGIS (free).

---

## 11. Ideas worth adding

Each of these fits in one to three sessions after the core is done, and each grows from data the site already has.

1. **Contemporaries.** "Who else was alive at the same time as Confucius?" brings out surprising overlaps, such as the Buddha, Pythagoras and Heraclitus around 500 BCE. This only needs a date query on existing records.
2. **Teacher and influence lines.** Wikidata records "student of" and "influenced by". Drawn as arcs on the map, these show ideas moving from Athens to Alexandria to Baghdad to Córdoba.
3. **How inventions spread.** Animate an invention's arrival from place to place, for example paper moving from China to Samarkand, then Baghdad, then Europe. Each step is a sourced record, which makes this a good kind of contribution for the community.
4. **Read the book.** Link literary works to free full texts on Project Gutenberg and Wikisource, so the map leads straight to reading.
5. **Guided stories written by contributors.** A story is an ordered list of years, map views and short texts, such as "The Silk Road" or "The Rise of Islam". It goes through the same review path as other content.
6. **Borders drawn with their uncertainty.** Blur or fade borders by precision, and show disputed borders as overlapping outlines with their sources. Very few history maps do this honestly. It suits your measurement background and could be written up as a short paper on visualizing uncertainty in historical GIS.
7. **Multilingual site.** Wikidata stores names in many languages. Community translators can add summaries per language, which widens the contributor base.
8. **Fix problems upstream.** Border errors your contributors find can be sent back to historical-basemaps as pull requests. That improves the shared dataset and is public evidence of open-source work.
9. **Classroom quiz.** "Which year is this map?" or "Who ruled here?" games built from the same data, for teachers.

---

## 12. Milestone summary

| Milestone | After session | What exists |
|---|---|---|
| v0.1 MVP | 5 | Public map, 14 border snapshots, time slider |
| v0.2 Open project | 8 | Licenses, rules, automatic checks, "Suggest an edit" with admin approval |
| v0.3 Content | 14 | People, works and inventions by period; contributions auto-publish after approval |
| v0.4 Polities | 17 | State cards, rulers, dynasty timeline |
| v0.5 Follow a country | 21 | Any modern country traced through time, area charts |
| v0.6 Environment | 24 | Land-use overlay and sourced environmental events |
| v1.0 | 28 | Tested, fast, searchable, citable open dataset |
| v2.0 Platform | 35 | On-site editing, moderation queue, per-record history, roles |

**Must have:** Phases 0–3. **Should have:** Phases 4, 5, 7. **Could have:** Phase 6. **When demand appears:** Phase 8. **Later:** section 11.

## 13. Known limitations and risks

- Borders are approximate snapshots and, for early periods, often show cultural zones rather than states with fixed borders.
- Wikidata coverage is biased toward well-documented, often European, figures. A sitelink filter strengthens that bias, so consider separate thresholds per region.
- Dates before about 1000 BCE are often uncertain by decades or more. Show the precision.
- **Community editing brings edit wars.** Borders and national histories are politically sensitive. The content policy, required sources and the "disputed" mechanism exist to handle this. Expect to use them.
- **Review is the bottleneck.** With one admin, contribution speed is limited by your free time. Recruiting one or two trusted reviewers early matters more than any feature.
