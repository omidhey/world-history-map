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
Wikidata again instead of using `raw/wikidata/`). The aim is philosophers whose **thought** is
studied, spread across traditions, not whoever is most famous.

**Who is imported**

1. Humans with occupation philosopher who have an article in the **Stanford Encyclopedia of
   Philosophy or the Internet Encyclopedia of Philosophy** (as recorded on Wikidata) and at least
   50 sitelinks: 263 people.
2. Everyone in the curated list [pipeline/philosophers_canon.json](../pipeline/philosophers_canon.json):
   212 people in 12 traditions (Chinese, Indian, Islamic, Iranian, Japanese, Korean, African,
   Jewish, Latin American, Stoic, plus major Western thinkers the encyclopedias' Wikidata links
   miss). Each is resolved through their English Wikipedia article title, not a name search, and
   each tradition links its Wikipedia overview. Add people by pull request.

Together 439 people; 9 already had a hand-written record (never changed), 16 were skipped, and
**414 new records** were written.

A first version (same day) took everyone with occupation philosopher and ≥ 80 sitelinks. That
measures fame, not thought: it brought in Emmanuel Macron, Harry Houdini and several popes, and
put only 29 of 335 people in Asia and 4 in Africa. Mencius, Mozi and Xunzi were missing entirely
because Wikidata gives no coordinates for their birthplaces.

**Spread** (by place): Europe 245, Asia 93, Americas 33, Middle East / North Africa 31,
Africa 12. By start century: 50 BCE, 112 from 1 to 1500 CE, 252 after 1500. The
encyclopedia threshold was compared at 30 / 40 / 50 / 60 sitelinks; 50 trims minor modern
Europeans while keeping every curated name.

**How facts are read**

- **Dates come from the entity data, not the query service.** The query service gives
  astronomical years (Socrates born `-0469`) and turns Julian dates into Gregorian ones (Cicero,
  born 3 January 106 BCE, lands in 107 BCE). A check of the first import against the entity data
  found 7 of 35 BCE records off by a year that way. The entity data keeps the year as entered,
  with no year 0. The script checks Socrates (470–399 BCE) and Confucius (551–479 BCE) before
  writing anything.
- Without a birth date, the floruit ("flourished") year is used and the record says `circa`.
- Only the best-ranked statements count (preferred, else normal; never deprecated). When they
  give different years the record is `disputed` with one claim per year (23 records); the main
  value is the year most statements give.
- `date_precision` follows Wikidata's: day, year (also for month), decade, century. Plato's
  preferred dates are decade-precision, so his record says "decade".
- **Location:** birthplace, else where the person worked, else where they died. A place without
  coordinates borrows those of the region it lies in. Where Wikidata has no usable place, the
  curated list may give one with the Wikipedia article that states it (Mencius: Zou, now
  Zoucheng; Mozi: Lu, now Tengzhou; Nimbarka: Mathura; also ready for Dharmakirti: Nalanda and
  Gaṅgeśa: Mithila, who are still skipped for their dates).
- Names are the English label, else Wikidata's language-neutral `mul` label.
- Summaries are a template built from the CC0 Wikidata description ("4th-century BCE Greek
  philosopher, born in Athens. Imported from Wikidata; a summary in our own words is still to be
  written."). The curated list can correct a wrong description, with a source (Kumārila Bhaṭṭa:
  Wikidata called him an alchemist). Rewriting summaries is open to contributors.
- Sources: the Wikidata item, the English Wikipedia article, and the SEP / IEP article when
  there is one.

**Still missing** (16 skipped). No usable place on Wikidata: Hui Shi, Gongsun Long, Yang Zhu,
Guo Xiang, Kanada, Kapila, Jaimini, Badarayana, Kundakunda, Seo Gyeong-deok, Mazdak, Hamid
al-Din al-Kirmani, Sextus Empiricus, Diogenes Laërtius; a sourced `place` in the curated list
brings them in. Unusable dates on Wikidata: Dharmakirti (death before birth), Gaṅgeśa (none);
those need fixing on Wikidata itself.

Existing records whose dates differ from Wikidata (reported, not changed): Gautama Buddha and
Laozi (Wikidata has century-precision dates).

## Scientists, writers and works from Wikidata (Session 12, 2026-10-28)

`python pipeline/import_wikidata.py --category scientist|writer|work` (repeatable; no flag runs all four categories). Dates, places and the Julian/BCE handling are the same as for philosophers.

- **Scientists**: humans with occupation scientist, a MacTutor biography and at least 80 sitelinks (147), plus [scientists_canon.json](../pipeline/scientists_canon.json) (347 names in 12 groups, including Islamic, Chinese, Indian, Japanese/Korean, African and Latin American science). 355 new records. MacTutor leans to mathematics and Europe, so the curated list carries the rest. Thresholds compared: 60 sitelinks gave 235 from MacTutor and 416 records, 80 gives 147 and 355.
- **Writers**: curated list only ([writers_canon.json](../pipeline/writers_canon.json), 486 names). An encyclopedia signal (Britannica, Gutenberg) gave 800 to 2,300 people at any sensible threshold, mostly Western. 428 new records.
- **Works**: curated list only ([works_canon.json](../pipeline/works_canon.json)). Date = publication, else inception, else the author's floruit (marked `circa`). Place = the list's place, else the author's (birth, work, death). The summary says "associated with" because that is the author's place, not necessarily where the work was written (the Odyssey lands on Ios, where Homer died per Wikidata). 222 new records; 86 skipped.
- Curated entries are Wikipedia article titles, resolved to Wikidata items through the Wikipedia API (redirects followed); titles that resolve to nothing are printed (Kim Sakkat, al-Maʿarri, Gulistan, Bustan, Rihla, Ihya, The Life of an Amorous Man, Nueva corónica, Canzoniere).
- **Spread** (place): scientists Europe 209, Asia 68, Americas 48, Middle East / N. Africa 24, Africa 4. Writers Europe 182, Asia 110, Americas 56, Middle East / N. Africa 49, Africa 31. Works Europe 105, Asia 46, Americas 40, Middle East / N. Africa 16, Africa 15. African science is thin: Wikidata gives few coordinates and the list is short; contributors can add names.
- **Skipped works** (86): mostly anonymous or collective texts with no author on Wikidata (Qur'an, Psalms, Ramayana, Popol Vuh) and so no place; a curated `place` with a source brings them in. Others have no date.
- Existing records that differ from Wikidata (reported, not changed): Homer (ours −800/−701, Wikidata −900/−800), Murasaki Shikibu (death 1014 vs 1100), Hafez (end), Tale of Genji (1008 vs 1010), Iliad (−750 vs −800), Shahnameh, Code of Hammurabi.
- Inventions are not imported: Wikidata structures them too poorly.

## Polities (Session 15, 2026-10-28)

`data/polities/` has 86 records for the most visible states, written from `pipeline/polities_seed.json`
by `pipeline/make_polities.py`. Choice: names in the border snapshots ranked by drawn area and number of
snapshots, then states, empires, kingdoms and caliphates picked by hand. Hunter-gatherer and culture
zones (about half of the 1,200 names) and most modern countries are left out; contributors can add them.
Every name was checked to exist in the snapshots. Summaries are written in our own words; dates are
round figures from Wikipedia, not yet checked against a second source.

Known gaps: only 86 of about 1,200 names have a card; modern countries (Egypt, Ghana, Mali)
have none yet.

## Spatial lineage (Session 18, 2026-10-29)

`pipeline/make_lineage.py` writes `data/lineage/<ADM0_A3>.json` (176 countries) plus `index.json`:
for each of the 14 snapshots, the historical states covering the country, with their share of its
area, largest first. Method: Natural Earth Admin-0 1:110m (public domain, pinned commit, via
`download_countries.py`) against our simplified snapshots, both in EPSG:6933 (equal-area), one
snapshot loaded at a time, overlapping parts of one state dissolved first. Countries are keyed by
`ADM0_A3` because `ISO_A3` is -99 for France and Norway. Antarctica is skipped. States under 1 % of
a country are summed into an `other` entry; unnamed land has `name: null`; pieces filled by
`carry_forward.py` keep `carried: <year>`. Runs in about 35 s. Needs `pipeline/requirements-lineage.txt`
(geopandas); the committed output means CI and Pages never need it.

Limits: 110m outlines omit microstates and are coarse for small countries; shares are of the
simplified snapshots; the source's overlapping polygons can make shares in one snapshot add up to
slightly over 1; a few carried pieces look odd (France 400: 13 % "Manioc farmers", carried from
323 BCE). Automatic results include noise; Session 20 adds curated overrides.

## Observations

- **Unnamed polygons are common**, especially early on (113 of 138 at 3000 BCE, 148 of 291 in 1500).
  They are land with no polity recorded. The map draws them in a neutral colour with no tooltip.
- **`BORDERPRECISION` is constant within a snapshot** in the files checked: every feature is 1
  in 3000 BCE and 1500, every feature is 3 in 2010. So "dashed = uncertain" currently marks whole
  eras rather than single borders.
- File names: upstream uses `world_bc323.geojson` for BCE; ours keep the sign (`world_-323.geojson`).
