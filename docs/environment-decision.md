# Environment layer: research and decision (Session 22)

Status: **conditional go** for one HYDE variable (Session 23), **blocked on one open question: the license** (see 2.2). Checked 2026-10-29.

## 1. What I checked, and what I could not

| Source | What I got | Reliability |
|---|---|---|
| [Our World in Data, cropland over the long term](https://ourworldindata.org/grapher/cropland-use-over-the-long-term) | HYDE **3.5 (2025)** replaces 3.4. 10,000 BCE to 2025 CE. 5 arc-minute grid (about 85 km² at the equator). Categories: cropland (irrigated/rainfed, rice/non-rice), grazing land, population, built-up area. 3.5 adds new radiocarbon/archaeological data on the onset of agriculture. 2023–2025 values are extrapolated. | Secondary (a redistributor), but it quotes the producer's description. |
| Web search summaries (OWID pages) | Grids are ArcMap ASCII; netCDF added as an extra format in 3.5. Suggested citation: Utrecht University / PBL, *History Database of the Global Environment (HYDE v3.5, 2025)*; methods paper for 3.2: Klein Goldewijk et al. 2017, *Earth System Science Data* 9, 927–953. | Secondary, not verified at the source. |
| HYDE data DOI `10.24416/UU01-F45D44` (landing page `public.yoda.uu.nl`) | **Not readable**: the page returned an access-denied bot check. `landuse.pbl.nl/data` also failed to load. | **Not verified.** |
| [PAGES 2k](https://catalog-beta.data.gov/dataset/noaa-wds-paleoclimatology-pages2k-common-era-surface-temperature-reconstructions) (climate reconstruction looked at) | Common Era (last 2,000 years) temperature reconstructions; the Arctic gridded product (Werner et al. 2018) is delivered as an ensemble of 600+ realisations, which is how it expresses uncertainty. Catalog records disagree on rights for some products (one CC0, one "otherRestrictions"). | Search summaries only; not downloaded. |

Not verified at the source: HYDE's license, exact file sizes, the exact list of time steps (OWID says there is no single uniform interval; the earlier HYDE 3.2 used 1000-year steps to 0 CE, 100-year steps to 1700, then 10-year steps — confirm for 3.5), and PAGES 2k's uncertainty method. Do not treat these as facts until Session 23 reads the dataset's own README.

## 2. Decisions

### 2.1 What we will show (if go)
- **One variable: HYDE cropland (share of each grid cell)**, drawn as a semi-transparent overlay on the existing map, switchable on/off. Cropland is the variable that best tells a history story (spread of farming) and needs the fewest outside assumptions. Population density is the alternative if cropland is too heavy.
- Only for the **same snapshot years the borders use** (or the nearest HYDE time step at or before), labelled "Land use as of …", exactly like "Borders as of …". No interpolation between time steps.
- Every overlay carries the label **"Model estimate (HYDE 3.5)"**, a legend with units, a link to the HYDE source and the citation.

### 2.2 License gate (blocks Session 23)
HYDE's terms were not readable. Before any HYDE-derived file enters the repository, read the terms on the DOI landing page (open it in a normal browser) and record them here. Compatibility to check: the site's code is GPL-3.0, human-written text CC BY-SA 4.0. Rendered PNG overlays are derived data and need the same attribution as the source. **If the terms forbid redistribution of derived images or are unclear, stop: no-go for Session 23, go straight to Session 24 (sourced events).**

### 2.3 What we will not claim
- No precise local values. At 5 arc-minutes and with modelled allocation, a pixel is not a measurement; the UI shows no per-pixel numbers.
- No causation (no "this empire fell because of drought"). Environmental records show conditions; they do not explain events.
- No certainty for early periods: before roughly 1 CE the estimates rest on sparse archaeological and radiocarbon evidence and population-scaling assumptions. The overlay says so.
- No climate layer in this version. PAGES 2k covers only 2,000 years, is coarse, and is delivered as an uncertainty ensemble, which the map would hide. Climate stays out until a source with a clear license and a simple way to show uncertainty exists.
- No data for 2023–2025 presented as observation (extrapolated).

### 2.4 Size and memory (8 GB laptop)
Plan for Session 23: read one ASCII grid at a time (a 5′ global grid is 4320 × 2160 ≈ 9.3 M cells, tens of MB as text), render a downsampled PNG, discard the grid. Target a few hundred KB per PNG, 14 PNGs; record before/after sizes in `docs/data-notes.md`. Raw downloads stay in git-ignored `raw/`.

### 2.5 Session 24 (events): criteria
Records use the existing schema and review path (`data/entries/`, sources required, disputed flag where dates differ). Candidates: drying of the Sahara, the 536 CE volcanic event, Little Ice Age, the shifting head of the Persian Gulf. Each needs at least one scholarly source and states uncertainty in its dates; summaries say what happened, not what it caused. This path needs no HYDE data, so it can proceed even if 2.2 fails.

## 3. Handoff to Session 23
1. Open the HYDE DOI in a browser, record license and the real time-step list here.
2. If allowed: download the cropland grids for the needed years into `raw/`, write `pipeline/make_overlays.py`, add the overlay toggle and label.
3. If not allowed: mark Session 23 skipped in `CHECKPOINTS.md` and continue with Session 24.
