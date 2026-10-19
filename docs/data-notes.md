# Data notes

## Border snapshots (Session 2, 2026-10-19)

Source: [historical-basemaps](https://github.com/aourednik/historical-basemaps), GPL-3.0,
pinned to commit `da7a4b7` in `pipeline/download_borders.py`.
Simplified with mapshaper 0.7.90: `-simplify 10% keep-shapes`, coordinates rounded to 0.0001°.

Re-create with `npm install` then `python pipeline/download_borders.py`.
`python pipeline/build_site.py` copies the result into `site/data/` for the page.

| Year | Raw KB | Simplified KB | Features |
|---:|---:|---:|---:|
| -3000 | 770 | 74 | 138 |
| -2000 | 838 | 85 | 145 |
| -1000 | 854 | 94 | 163 |
| -500 | 894 | 99 | 189 |
| -323 | 868 | 93 | 149 |
| -1 | 1157 | 166 | 442 |
| 400 | 1096 | 150 | 367 |
| 800 | 954 | 120 | 225 |
| 1200 | 1026 | 136 | 286 |
| 1500 | 1142 | 143 | 291 |
| 1800 | 1600 | 342 | 627 |
| 1914 | 1259 | 117 | 177 |
| 1945 | 1527 | 131 | 227 |
| 2010 | 1849 | 177 | 240 |
| **Total** | **15834** | **1927** | |

The roadmap estimated "a few hundred KB per file"; the measured size is 74–342 KB,
about 8–21 % of the original. 1800 is the largest (627 features).

## Observations

- **Unnamed polygons are common**, especially early on (113 of 138 at 3000 BCE, 148 of 291 in 1500).
  They are land with no polity recorded. The map draws them in a neutral colour with no tooltip.
- **`BORDERPRECISION` is constant within a snapshot** in the files checked: every feature is 1
  in 3000 BCE and 1500, every feature is 3 in 2010. So "dashed = uncertain" currently marks whole
  eras rather than single borders.
- File names: upstream uses `world_bc323.geojson` for BCE; ours keep the sign (`world_-323.geojson`).
