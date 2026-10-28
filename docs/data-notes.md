# Data notes

## Border snapshots (Session 2, 2026-10-19)

Source: [historical-basemaps](https://github.com/aourednik/historical-basemaps), GPL-3.0,
pinned to commit `da7a4b7` in `pipeline/download_borders.py`.
Simplified with mapshaper 0.7.90: every realm is split into its parts, simplified with
`-simplify 10% keep-shapes`, then put back together, so no island larger than ~600 km² is lost.
Sourced corrections from `data/borders/overrides.json` are applied afterwards (see
[vanished-realms.md](vanished-realms.md)).

Re-create with `npm install`, `pip install -r pipeline/requirements.txt`, then
`python pipeline/download_borders.py`. `python pipeline/build_site.py` copies the result into
`site/data/` for the page.

| Year | Raw KB | Output KB | Features | Carried forward (sq. degrees) |
|---:|---:|---:|---:|---:|
| -3000 | 770 | 133 | 138 | 0 |
| -2000 | 838 | 163 | 148 | 136 |
| -1000 | 854 | 186 | 170 | 29 |
| -500 | 894 | 215 | 218 | 2369 |
| -323 | 868 | 234 | 194 | 3129 |
| -1 | 1157 | 485 | 503 | 3890 |
| 400 | 1096 | 461 | 450 | 3979 |
| 800 | 954 | 278 | 265 | 2197 |
| 1200 | 1026 | 299 | 323 | 1169 |
| 1500 | 1142 | 396 | 339 | 2413 |
| 1800 | 1600 | 601 | 675 | 2289 |
| 1914 | 1259 | 249 | 180 | 0 |
| 1945 | 1527 | 268 | 231 | 1 |
| 2010 | 1849 | 341 | 245 | 5 |
| **Total** | **15834** | **4309** | | |

Output sizes include the carried-forward areas (see [vanished-realms.md](vanished-realms.md),
section 6). The largest file is 1800 at 601 KB.

History: the first version (also 2026-10-19) rounded coordinates and simplified realms whole. It
came to 1.9 MB in total but lost 149 features in 1 BCE and dozens of islands per snapshot.

## Philosophers from Wikidata (Session 11, 2026-10-28)

`python pipeline/import_wikidata.py` (add `--dry-run` to see the report only, `--refresh` to ask
Wikidata again instead of using `raw/wikidata/`). It selects humans with occupation philosopher
(Q4964182), a birth date, a birthplace with coordinates and **at least 80 sitelinks**: 350 items
on 2026-10-28. 13 already had a hand-written record and were left alone; 2 have only "unknown
value" as birth date (Patanjali, Adrian IV) and were skipped; **335 new records** were written.

- **Dates come from the entity data, not the query service.** The query service gives
  astronomical years (Socrates born `-0469`) and turns Julian dates into Gregorian ones (Cicero,
  born 3 January 106 BCE, lands in 107 BCE). A check of the first import against the entity data
  found 7 of 35 BCE records off by a year that way. The entity data keeps the year as entered,
  with no year 0. The script checks Socrates (470–399 BCE) and Confucius (551–479 BCE) before
  writing anything.
- Only the best-ranked statements count (preferred, else normal; never deprecated). When they
  give different years the record is `disputed` with one claim per year (12 records); the main
  value is the year most statements give.
- `date_precision` follows Wikidata's: day, year (also for month), decade, century. Plato's
  preferred dates are decade-precision, so his record says "decade".
- Location is the birthplace, labelled in English, else Wikidata's language-neutral `mul` label.
- Summaries are a template built from the CC0 Wikidata description ("4th-century BCE Greek
  philosopher, born in Athens. Imported from Wikidata; a summary in our own words is still to be
  written."). Rewriting them is open to contributors.
- Existing records whose dates differ from Wikidata (reported, not changed): Gautama Buddha and
  Laozi (Wikidata has century-precision dates), Murasaki Shikibu (Wikidata 970–1100).
- **Bias:** by birthplace, 260 Europe, 29 Asia, 25 Americas, 17 Middle East / North Africa,
  4 Africa; 212 of the 335 were born after 1700. A sitelink threshold favours well-documented
  European figures (roadmap, section 13). Lower regional thresholds are a later option.

## Observations

- **Unnamed polygons are common**, especially early on (113 of 138 at 3000 BCE, 148 of 291 in 1500).
  They are land with no polity recorded. The map draws them in a neutral colour with no tooltip.
- **`BORDERPRECISION` is constant within a snapshot** in the files checked: every feature is 1
  in 3000 BCE and 1500, every feature is 3 in 2010. So "dashed = uncertain" currently marks whole
  eras rather than single borders.
- File names: upstream uses `world_bc323.geojson` for BCE; ours keep the sign (`world_-323.geojson`).
