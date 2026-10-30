# Performance (Session 26, 2026-10-30)

Question: is the page fast enough, and does TopoJSON help? Sizes below are measured on the files in `data/borders/` and `site/data/`; gzip is Python's default level, close to what GitHub Pages serves.

## What changed

The page already loaded only the snapshot in view (plus its two neighbours, cached). The border files are now converted to **TopoJSON** at build time (`build_site.py`, mapshaper, `quantization=100000`) and turned back into GeoJSON in the browser with `topojson-client` 3.1.0 (8 KB, `site/vendor/topojson/`). `data/borders/` stays GeoJSON, the source of truth.

## Border snapshots (KB)

| Year | GeoJSON | GeoJSON gzip | TopoJSON | TopoJSON gzip |
|---:|---:|---:|---:|---:|
| -3000 | 133 | 46 | 55 | 14 |
| -2000 | 163 | 55 | 67 | 18 |
| -1000 | 186 | 62 | 76 | 21 |
| -500 | 215 | 69 | 89 | 25 |
| -323 | 234 | 77 | 97 | 28 |
| -1 | 485 | 158 | 203 | 57 |
| 400 | 461 | 151 | 193 | 55 |
| 800 | 278 | 92 | 118 | 33 |
| 1200 | 299 | 96 | 127 | 34 |
| 1500 (start view) | 396 | 131 | 158 | 47 |
| 1800 (largest) | 601 | 198 | 273 | 78 |
| 1914 | 249 | 87 | 90 | 28 |
| 1945 | 268 | 93 | 98 | 30 |
| 2010 | 341 | 115 | 120 | 36 |
| **All 14** | **4316** | **1438** | **1771** | **511** |

Over the wire (gzip) the starting view's borders shrink from 131 KB to 47 KB, and the largest snapshot from 198 KB to 78 KB (about 64 %).

## Other files (KB, raw / gzip)

entries.json 779 / 123, countries.json 156 / 47, polities.json 44 / 10, rulers.json 69 / 9, areas.json 16 / 2, Leaflet 148 (raw), page JS modules 35 (raw). Lineage files (1 MB in total) load one country at a time. At start the page now transfers roughly 0.3 MB gzipped, of which `entries.json` is the biggest part; the border files are no longer the largest item.

## Parse cost (Node, not a browser)

Parsing TopoJSON and converting to GeoJSON took 2–10 ms per snapshot, about the same as parsing the GeoJSON file (3–12 ms; 1800: 6 vs 12 ms). So the smaller download is not paid for in CPU time.

## What the conversion costs

- Quantisation to a 100,000-step grid drops 7 features in the whole set that were zero-area slivers (for example one unnamed sliver in 1 BCE and "Saharan pastoral nomads" at 323 BCE, a near-zero-width sliver in the source). They had no visible area. Property values of all other features are identical (checked for all 14 snapshots).
- The build now needs Node and `npm ci` (the Pages workflow installs them).

## Leaflet verdict: not measured

Not measured in a browser: the browser pane could not open localhost this session, so there are no draw or slider timings. Nothing in the numbers above suggests a problem (largest snapshot is 675 features, 273 KB), but "Leaflet is fast enough" is **unproven**; the MapLibre switch from the roadmap stays off the table until someone measures `show()` at 1800 on a slow phone. To do it: open the page, run `performance.now()` around a slider change to 1800 in the console.

## Not done

- No browser check of the TopoJSON loader (slider, cards, Follow a country); the conversion was checked in Node only.
- No lazy loading of `entries.json` (123 KB gzipped); worth it only if the dataset grows several times.
