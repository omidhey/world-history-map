# Environment layer: research and decision (Session 22)

Status: **conditional go** for one HYDE variable (Session 23), **blocked on one open question: the license is stated three different ways** (see 2.2). Checked 2026-10-29.

## 1. What I checked, and what I could not

| Source | What I got | Reliability |
|---|---|---|
| [Our World in Data, cropland over the long term](https://ourworldindata.org/grapher/cropland-use-over-the-long-term) | HYDE **3.5 (2025)** replaces 3.4. 10,000 BCE to 2025 CE. 5 arc-minute grid (about 85 km² at the equator). Categories: cropland (irrigated/rainfed, rice/non-rice), grazing land, population, built-up area. 3.5 adds new radiocarbon/archaeological data on the onset of agriculture. 2023–2025 values are extrapolated. | Secondary (a redistributor), but it quotes the producer's description. |
| Web search summaries (OWID pages) | Grids are ArcMap ASCII; netCDF added as an extra format in 3.5. Suggested citation: Utrecht University / PBL, *History Database of the Global Environment (HYDE v3.5, 2025)*; methods paper for 3.2: Klein Goldewijk et al. 2017, *Earth System Science Data* 9, 927–953. | Secondary, not verified at the source. |
| HYDE data DOI `10.24416/UU01-F45D44` (landing page `public.yoda.uu.nl`) | **Not readable**: the page returned an access-denied bot check. `landuse.pbl.nl/data` also failed to load. | **Not verified.** |
| [PAGES 2k](https://catalog-beta.data.gov/dataset/noaa-wds-paleoclimatology-pages2k-common-era-surface-temperature-reconstructions) (climate reconstruction looked at) | Common Era (last 2,000 years) temperature reconstructions; the Arctic gridded product (Werner et al. 2018) is delivered as an ensemble of 600+ realisations, which is how it expresses uncertainty. Catalog records disagree on rights for some products (one CC0, one "otherRestrictions"). | Search summaries only; not downloaded. |

Files downloaded by the owner from the dataset page (2026-10-29): `readme_HYDE_3.5.txt` (release March 2025), two `yoda-metadata` exports, and `License.txt`. From the README: grids are ASCII, 4320 × 2160 cells, `cellsize 0.0833333`, `NODATA_value -9999`; `cropland<yr>.asc` is cropland km² per grid cell; time steps are **1000 years in the BCE period, 100 years to 1700, 10 years to 2000, then yearly**; each release has baseline, lower and upper scenarios. Other variables: `popd` (density), `grazing`, `uopp` (built-up).

Still not verified: exact file sizes, and PAGES 2k's uncertainty method. Do not treat these as facts until Session 23 reads the dataset's own README.

## 2. Decisions

### 2.1 What we will show (if go)
- **One variable: HYDE cropland (share of each grid cell)**, drawn as a semi-transparent overlay on the existing map, switchable on/off. Cropland is the variable that best tells a history story (spread of farming) and needs the fewest outside assumptions. Population density is the alternative if cropland is too heavy.
- Only for the **HYDE time step at or before each border snapshot**, labelled "Land use as of …", exactly like "Borders as of …". No interpolation between time steps. Because BCE steps are 1000 years apart, snapshots at -500 and -323 would show the -1000 grid, and -1 would show 1 CE (check whether HYDE files use year 0 or 1 CE); the label must state the HYDE year actually shown. Use the baseline scenario only.
- Every overlay carries the label **"Model estimate (HYDE 3.5)"**, a legend with units, a link to the HYDE source and the citation.

### 2.2 License gate (blocks Session 23)
The files give **three different licenses** for HYDE 3.5:

| File | License stated |
|---|---|
| `yoda-metadata[1749214948].txt` ("HYDE data for the Global Carbon Budget (2025)") | CC BY-**NonCommercial** 4.0 |
| `yoda-metadata[1790593895].txt` (same title) | CC BY 4.0 |
| `readme_HYDE_3.5.txt` | CC BY 3.0 ("applies to all of the HYDE data") |
| `License.txt` | text of CC BY 4.0 |

CC BY (3.0 or 4.0) allows republishing derived images with attribution and a note that we modified the data. **CC BY-NC would not work**: the project promises open reuse (GPL code, CC BY-SA text), and an NC-only layer could not be mixed into it or reused commercially downstream. Two metadata versions of one record differing on exactly this word suggests the NC one is an older or draft version, but that is a guess. Also, the metadata title is "for the Global Carbon Budget", which may be a different package from the main HYDE 3.5 release.

**Resolved 2026-10-29:** the owner read the dataset landing page (doi.org/10.24416/UU01-F45D44) and its License field says *Creative Commons Attribution 4.0 International Public License*. The NC metadata file was therefore an older/other version. Session 23 may proceed. Keep the NC file's existence in mind: re-check the field when downloading, and note the downloaded package name here.

*Original rule, kept for the record:* Session 23 proceeds only if the *current* landing page (and ideally the dataset's author, Kees Klein Goldewijk, c.g.m.kleingoldewijk@uu.nl) confirms CC BY. Record the confirmed license, date and the exact package downloaded here. If it is NC or stays unclear: no-go for Session 23, go straight to Session 24 (sourced events). Attribution if CC BY: cite Klein Goldewijk et al. (HYDE 3.5), link the DOI, and label overlays "derived from HYDE 3.5, downsampled".

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
1. Confirm the license (see 2.2) and record it here.
2. If allowed: download the cropland grids for the needed years into `raw/`, write `pipeline/make_overlays.py`, add the overlay toggle and label.
3. If not allowed: mark Session 23 skipped in `CHECKPOINTS.md` and continue with Session 24.
