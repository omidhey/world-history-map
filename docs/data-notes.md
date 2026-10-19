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

| Year | Raw KB | Simplified KB | Features |
|---:|---:|---:|---:|
| -3000 | 770 | 133 | 138 |
| -2000 | 838 | 160 | 145 |
| -1000 | 854 | 174 | 163 |
| -500 | 894 | 180 | 189 |
| -323 | 868 | 183 | 150 |
| -1 | 1157 | 359 | 442 |
| 400 | 1096 | 317 | 368 |
| 800 | 954 | 222 | 226 |
| 1200 | 1026 | 261 | 287 |
| 1500 | 1142 | 318 | 292 |
| 1800 | 1600 | 529 | 627 |
| 1914 | 1259 | 242 | 177 |
| 1945 | 1527 | 263 | 228 |
| 2010 | 1849 | 330 | 240 |
| **Total** | **15834** | **3671** | |

The roadmap estimated "a few hundred KB per file"; the measured size is 133–529 KB, about
17–33 % of the original. 1800 is the largest (627 features).

History: the first version (also 2026-10-19) rounded coordinates and simplified realms whole. It
came to 1.9 MB in total but lost 149 features in 1 BCE and dozens of islands per snapshot.

## Observations

- **Unnamed polygons are common**, especially early on (113 of 138 at 3000 BCE, 148 of 291 in 1500).
  They are land with no polity recorded. The map draws them in a neutral colour with no tooltip.
- **`BORDERPRECISION` is constant within a snapshot** in the files checked: every feature is 1
  in 3000 BCE and 1500, every feature is 3 in 2010. So "dashed = uncertain" currently marks whole
  eras rather than single borders.
- File names: upstream uses `world_bc323.geojson` for BCE; ours keep the sign (`world_-323.geojson`).
