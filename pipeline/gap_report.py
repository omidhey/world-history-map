"""Find realms that vanish from a snapshot and come back later, and show who held their land meanwhile.

For each NAME that is missing in a snapshot between two snapshots where it exists, the script takes
its territory from the nearest earlier snapshot and measures which polygons of the gap snapshot
cover it. Uncovered land (sea in that snapshot) is ignored.

Run from the repository root:  python pipeline/gap_report.py [--json out.json]
Needs shapely (pip install -r pipeline/requirements.txt).
"""

import argparse
import json
from pathlib import Path

from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
BORDERS = ROOT / "data" / "borders"
UNNAMED = "(unnamed)"


def load_snapshots():
    manifest = json.loads((BORDERS / "manifest.json").read_text(encoding="utf-8"))
    snapshots = []
    for entry in manifest["snapshots"]:
        geojson = json.loads((BORDERS / entry["file"]).read_text(encoding="utf-8"))
        features = []
        for index, feature in enumerate(geojson["features"]):
            if not feature["geometry"]:
                continue  # a few features lose all geometry in simplification
            geometry = shape(feature["geometry"]).buffer(0)  # repair self-intersections from simplification
            if not geometry.is_empty:
                features.append((index, feature["properties"], geometry))
        snapshots.append((entry["year"], features))
    return snapshots


def territory(features, name):
    return unary_union([g for _, p, g in features if p.get("NAME") == name])


def holders(features, region, min_share=0.05):
    """Polygons of a snapshot covering `region`, largest share first (shares of the region's area)."""
    total = region.area
    found = []
    for index, properties, geometry in features:
        if not geometry.intersects(region):
            continue
        share = geometry.intersection(region).area / total
        if share >= min_share:
            found.append({
                "feature": index,
                "name": properties.get("NAME") or UNNAMED,
                "subjecto": properties.get("SUBJECTO"),
                "share": round(share, 2),
            })
    return sorted(found, key=lambda h: -h["share"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="also write the report as JSON")
    args = parser.parse_args()

    snapshots = load_snapshots()
    years = [year for year, _ in snapshots]
    present = {}
    for i, (_, features) in enumerate(snapshots):
        for _, properties, _ in features:
            if properties.get("NAME"):
                present.setdefault(properties["NAME"], set()).add(i)

    report = []
    for name in sorted(present):
        indices = sorted(present[name])
        gaps = [i for i in range(indices[0], indices[-1] + 1) if i not in present[name]]
        for gap in gaps:
            before = max(i for i in indices if i < gap)
            region = territory(snapshots[before][1], name)
            found = holders(snapshots[gap][1], region)
            report.append({"name": name, "year": years[gap], "shape_from": years[before], "holders": found})
            summary = ", ".join(f"{h['name']} [{h['subjecto']}] {h['share']:.0%}" for h in found) or "sea / nothing"
            print(f"{name} @ {years[gap]} (shape from {years[before]}): {summary}")

    if args.json:
        args.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
