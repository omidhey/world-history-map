"""The TopoJSON written by build_site.to_topojson keeps every feature and its properties."""

import json
import shutil
from pathlib import Path

import pytest

import build_site

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS = ["world_-3000.geojson", "world_1800.geojson"]  # smallest and largest by feature count


@pytest.fixture(scope="module")
def mapshaper():
    if not ((ROOT / "node_modules" / ".bin").exists() or shutil.which("npx")):
        pytest.skip("mapshaper not installed (npm ci)")
    return build_site.find_mapshaper()


@pytest.mark.parametrize("name", SNAPSHOTS)
def test_round_trip_keeps_features_and_properties(mapshaper, tmp_path, name):
    source = ROOT / "data" / "borders" / name
    out_name = build_site.to_topojson(mapshaper, source, tmp_path)
    assert out_name == source.stem + ".topo.json"
    original = json.loads(source.read_text(encoding="utf-8"))["features"]
    topology = json.loads((tmp_path / out_name).read_text(encoding="utf-8"))
    geometries = next(iter(topology["objects"].values()))["geometries"]
    assert len(geometries) == len(original)
    assert [g.get("properties") for g in geometries] == [f["properties"] for f in original]
