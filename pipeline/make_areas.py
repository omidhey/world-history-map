"""Territory over time: for each polity and each border snapshot, the area of the land labelled with
the polity's border names, and what it gained and lost since the previous snapshot.

Areas are computed in an equal-area projection (EPSG:6933), one snapshot at a time. Land carried
forward by carry_forward.py (the pale "last recorded" realm) is counted separately, so a chart can
tell recorded territory from assumed territory. Gained/lost compare the polity's land at two
consecutive snapshots (geometry difference), and only exist when the polity is present in both.

Writes data/areas/areas.json ({polity_id: {"<year>": {...}}}), whole km2, deterministic.

Run from the repository root (needs geopandas, see requirements-lineage.txt):
  .venv/Scripts/python pipeline/make_areas.py
"""

import json
import time
from pathlib import Path

from make_lineage import BORDERS, ROOT, load_states

POLITIES = ROOT / "data" / "polities"
OUT = ROOT / "data" / "areas" / "areas.json"


def km2(geometry) -> int:
    return round(geometry.area / 1e6)


def main() -> None:
    started = time.time()
    manifest = json.loads((BORDERS / "manifest.json").read_text(encoding="utf-8"))
    polities = {}
    for path in sorted(POLITIES.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        polities[record["id"]] = set(record["border_names"])

    result = {pid: {} for pid in polities}
    previous = {}  # polity id -> its (recorded + carried) geometry at the previous snapshot
    for snapshot in manifest["snapshots"]:
        year = str(snapshot["year"])
        states = load_states(BORDERS / snapshot["file"])
        current = {}
        for pid, names in polities.items():
            rows = states[states["NAME"].isin(names)]
            if rows.empty:
                continue
            recorded = rows[rows["CARRIED"] == -99999]
            carried = rows[rows["CARRIED"] != -99999]
            whole = rows.geometry.union_all()
            entry = {
                "area_km2": km2(recorded.geometry.union_all()) if len(recorded) else 0,
                "carried_km2": km2(carried.geometry.union_all()) if len(carried) else 0,
            }
            if pid in previous:
                entry["gained_km2"] = km2(whole.difference(previous[pid]))
                entry["lost_km2"] = km2(previous[pid].difference(whole))
            current[pid] = whole
            result[pid][year] = entry
        previous = current
        print(f"  {year}: {len(current)} polities present")
        del states

    result = {pid: years for pid, years in result.items() if years}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(result)} polities to {OUT} in {time.time() - started:.0f} s")


if __name__ == "__main__":
    main()
