"""Spatial lineage: for each modern country and each border snapshot, which historical states
covered it and what share of its area each covered.

Matching is by area, not by name, because names change (Elam, Media, Achaemenid ... for Iran).
Areas are computed in an equal-area projection (EPSG:6933). One snapshot is loaded at a time.

Writes data/lineage/<ADM0_A3>.json for every country plus data/lineage/index.json. The output is
automatic (source "automatic"); curated files override it later. Deterministic: re-running writes
identical files.

Run from the repository root:
  .venv/Scripts/python pipeline/download_countries.py
  .venv/Scripts/python pipeline/make_lineage.py
Needs `pip install -r pipeline/requirements-lineage.txt` (geopandas).
"""

import json
import time
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
COUNTRIES = ROOT / "raw" / "countries" / "ne_110m_admin_0_countries.geojson"
BORDERS = ROOT / "data" / "borders"
OUT = ROOT / "data" / "lineage"

EQUAL_AREA = "EPSG:6933"
MIN_SHARE = 0.01  # states covering less than 1 % of a country are slivers; summed into "other"
SKIP = {"ATA"}  # Antarctica: no permanent population, left out like in carry_forward.py


def load_countries() -> gpd.GeoDataFrame:
    countries = gpd.read_file(COUNTRIES)
    # ISO_A3 is -99 for France, Norway and a few others; ADM0_A3 is always set.
    countries = countries[~countries["ADM0_A3"].isin(SKIP)]
    countries = countries[["ADM0_A3", "NAME", "geometry"]].rename(columns={"ADM0_A3": "iso"})
    countries = countries.to_crs(EQUAL_AREA)
    countries["geometry"] = countries.geometry.make_valid()
    countries["area"] = countries.geometry.area
    return countries.sort_values("iso").reset_index(drop=True)


def load_states(path: Path) -> gpd.GeoDataFrame:
    """One row per (name, ruling power, carried-from year); overlapping parts dissolved."""
    states = gpd.read_file(path)
    states = states[states.geometry.notna() & ~states.geometry.is_empty].copy()
    for column in ("NAME", "SUBJECTO", "CARRIED"):
        if column not in states:
            states[column] = None
    states = states.to_crs(EQUAL_AREA)
    states["geometry"] = states.geometry.make_valid()  # projecting can make rings cross
    states["NAME"] = states["NAME"].where(states["NAME"].notna(), "")
    states["SUBJECTO"] = states["SUBJECTO"].where(states["SUBJECTO"].notna(), "")
    states["CARRIED"] = states["CARRIED"].where(states["CARRIED"].notna(), -99999)
    dissolved = states.dissolve(by=["NAME", "SUBJECTO", "CARRIED"], as_index=False)
    return dissolved[["NAME", "SUBJECTO", "CARRIED", "geometry"]]


def shares_for_snapshot(countries: gpd.GeoDataFrame, states: gpd.GeoDataFrame) -> dict:
    """iso -> sorted list of {name, subjecto, share[, carried]}."""
    result = {}
    tree = states.sindex
    for country in countries.itertuples():
        rows = []
        for index in sorted(tree.query(country.geometry, predicate="intersects")):
            state = states.iloc[index]
            area = state.geometry.intersection(country.geometry).area
            share = area / country.area
            if share > 0:
                rows.append((state, share))
        entries, other = [], 0.0
        for state, share in rows:
            if share < MIN_SHARE:
                other += share
                continue
            entry = {"name": state.NAME or None, "subjecto": state.SUBJECTO or None, "share": round(share, 4)}
            if state.CARRIED != -99999:
                entry["carried"] = int(state.CARRIED)
            entries.append(entry)
        entries.sort(key=lambda e: (-e["share"], e["name"] or "", e["subjecto"] or ""))
        if other >= 0.00005:
            entries.append({"name": "other", "subjecto": None, "share": round(other, 4), "other": True})
        result[country.iso] = entries
    return result


def main() -> None:
    started = time.time()
    manifest = json.loads((BORDERS / "manifest.json").read_text(encoding="utf-8"))
    countries = load_countries()
    lineage = {iso: {} for iso in countries["iso"]}
    for snapshot in manifest["snapshots"]:
        year = snapshot["year"]
        states = load_states(BORDERS / snapshot["file"])
        for iso, entries in shares_for_snapshot(countries, states).items():
            lineage[iso][str(year)] = entries
        print(f"  {year}: {len(states)} states")
        del states

    OUT.mkdir(parents=True, exist_ok=True)
    index = {}
    for country in countries.itertuples():
        area_km2 = round(country.area / 1e6)
        record = {
            "country": country.iso,
            "name": country.NAME,
            "area_km2": area_km2,
            "source": "automatic",
            "snapshots": lineage[country.iso],
        }
        (OUT / f"{country.iso}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        index[country.iso] = {"name": country.NAME, "area_km2": area_km2}
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {len(index)} countries to {OUT} in {time.time() - started:.0f} s")


if __name__ == "__main__":
    main()
