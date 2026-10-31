# Changelog

Each phase of `CHECKPOINTS.md` ends in a version. Dates are in the checkpoint entries.

## 1.0.0 (2026-10-31)
- Search over entries and states (Fuse.js) and shareable links (`?year=&country=&layers=&entry=`).
- TopoJSON borders (about 64 % smaller over the wire); site JavaScript split into ES modules; pytest and node tests with a CI job.
- About page with sources, licenses and limitations; contributor list from git history; `CITATION.cff` and `.zenodo.json` for citable releases.

## 0.6
- Environmental events as a ninth entry category (12 sourced records). A HYDE cropland overlay was built, then removed from the site; its files are kept in `data/overlays/`.

## 0.5
- Follow a country through time: spatial lineage for 176 countries, 10 curated, territory-over-time chart.

## 0.4
- 86 polity cards, 17 states with dynasties and rulers, and a timeline strip.

## 0.3
- Content layers: philosophers, scientists, writers and works imported from Wikidata plus curated records.

## 0.2
- Open-source foundation: licenses, content policy, issue forms, validation in CI.

## 0.1
- MVP: 14 border snapshots on a Leaflet map with a time slider, published on GitHub Pages.
