"""Copy the data the web page needs into site/data/ (generated, git-ignored):
border snapshots, and data/entries/ and data/polities/ merged into entries.json and
polities.json by pipeline/build.py.

Run from the repository root:  python pipeline/build_site.py
The GitHub Pages workflow runs the same script before publishing site/.
"""

import json
import shutil
from pathlib import Path

from build import build_entries, build_polities

ROOT = Path(__file__).resolve().parent.parent
COUNTRIES_IN = ROOT / "raw" / "countries" / "ne_110m_admin_0_countries.geojson"
BORDERS_IN = ROOT / "data" / "borders"
BORDERS_OUT = ROOT / "site" / "data" / "borders"


def _round(coords):
    if isinstance(coords[0], (int, float)):
        return [round(c, 2) for c in coords]
    return [_round(c) for c in coords]


def build_countries() -> int:
    """site/data/countries.json: outlines of the countries that have a lineage file, for "Follow a country"."""
    index_path = ROOT / "data" / "lineage" / "index.json"
    if not (COUNTRIES_IN.exists() and index_path.exists()):
        print("No country outlines or lineage index; run download_countries.py and make_lineage.py to enable Follow a country")
        return 0
    index = json.loads(index_path.read_text(encoding="utf-8"))
    features = []
    for f in json.loads(COUNTRIES_IN.read_text(encoding="utf-8"))["features"]:
        iso = f["properties"]["ADM0_A3"]
        if iso in index:
            geometry = {"type": f["geometry"]["type"], "coordinates": _round(f["geometry"]["coordinates"])}
            features.append({"type": "Feature", "properties": {"iso": iso}, "geometry": geometry})
    out = ROOT / "site" / "data" / "countries.json"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(features)} country outlines ({out.stat().st_size // 1024} KB)")
    return len(features)


def main() -> None:
    if BORDERS_OUT.exists():
        shutil.rmtree(BORDERS_OUT)
    BORDERS_OUT.mkdir(parents=True)

    manifest = json.loads((BORDERS_IN / "manifest.json").read_text(encoding="utf-8"))
    for snapshot in manifest["snapshots"]:
        shutil.copy2(BORDERS_IN / snapshot["file"], BORDERS_OUT / snapshot["file"])
    shutil.copy2(BORDERS_IN / "manifest.json", BORDERS_OUT / "manifest.json")
    lineage_in = ROOT / "data" / "lineage"
    if lineage_in.exists():
        lineage_out = ROOT / "site" / "data" / "lineage"
        if lineage_out.exists():
            shutil.rmtree(lineage_out)
        shutil.copytree(lineage_in, lineage_out)
        print(f"Copied {len(list(lineage_in.glob('*.json')))} lineage files to {lineage_out}")
    print(f"Copied {len(manifest['snapshots'])} snapshots to {BORDERS_OUT}")
    print(f"Wrote {build_entries()} entries to site/data/entries.json")
    print(f"Wrote {build_polities()} polities to site/data/polities.json")
    build_countries()


if __name__ == "__main__":
    main()
