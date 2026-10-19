# World History Map

An open-source, community-edited map of the world from about 3000 BCE to today.
Explore borders, rulers, thinkers, works and inventions period by period.

Status: early development. See [CHECKPOINTS.md](CHECKPOINTS.md) for progress and
[docs/roadmap.md](docs/roadmap.md) for the full plan.

## Run it locally (Windows)

Double-click `run_site.bat`, or:

```
python pipeline/build_site.py
cd site
python -m http.server 8000
```

then open http://localhost:8000. Opening `index.html` directly does not work,
because browsers block loading local data files from `file://`.

Live site (after the first deploy): https://omidhey.github.io/world-history-map/

## Updating the border data

```
npm install
python pipeline/download_borders.py
```

This downloads 14 snapshots into `raw/`, simplifies them with mapshaper into
`data/borders/` and rewrites `data/borders/manifest.json`. Sizes are in
[docs/data-notes.md](docs/data-notes.md).

## Folder layout

| Folder | Contents |
|---|---|
| `data/` | Source of truth, edited by contributors (one JSON file per record) |
| `pipeline/` | Python scripts: download, validate, build |
| `site/` | The web page. `site/data/` is generated, not edited |
| `docs/` | Decisions, schema, data notes, roadmap |
| `raw/` | Downloads (git-ignored) |

## Credits

- Historical borders: [historical-basemaps](https://github.com/aourednik/historical-basemaps)
  by A. Ourednik, GPL-3.0. Borders are approximate.
- Map library: [Leaflet](https://leafletjs.com) 1.9.4, BSD-2-Clause (bundled in `site/vendor/leaflet/`).
