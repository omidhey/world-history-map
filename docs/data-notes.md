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

## Observations

- **Unnamed polygons are common**, especially early on (113 of 138 at 3000 BCE, 148 of 291 in 1500).
  They are land with no polity recorded. The map draws them in a neutral colour with no tooltip.
- **`BORDERPRECISION` is constant within a snapshot** in the files checked: every feature is 1
  in 3000 BCE and 1500, every feature is 3 in 2010. So "dashed = uncertain" currently marks whole
  eras rather than single borders.
- File names: upstream uses `world_bc323.geojson` for BCE; ours keep the sign (`world_-323.geojson`).
