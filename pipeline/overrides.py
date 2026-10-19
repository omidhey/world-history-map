"""Apply data/borders/overrides.json: sourced corrections on top of the upstream border snapshots.

Operations (each entry names one snapshot `year`):
  rename  set properties on the feature with NAME == match.name (null = unnamed) that contains match.point
  carve   cut the territory that `shape_from` had out of the `hosts` features and make it a new feature
  copy    copy the `shape_from` feature into this snapshot as a new feature
Every changed or new feature gets OVERRIDE (the entry id), NOTE and SOURCES, so the map can say so.

Called by download_borders.py after simplification. Needs shapely.
"""

import json
from pathlib import Path

from shapely.geometry import Point, mapping, shape
from shapely.ops import unary_union

MIN_AREA = 0.01  # square degrees; smaller carve results are slivers from differing simplifications


def _geometry(feature):
    return shape(feature["geometry"]).buffer(0) if feature["geometry"] else None


def _territory(path: Path, name: str):
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    found = [
        _geometry(f) for f in features
        if f["properties"].get("NAME") == name and f["geometry"] and "CARRIED" not in f["properties"]
    ]
    if not found:
        raise ValueError(f"{path.name}: no feature named {name!r}")
    return unary_union(found)


def _polygonal(geometry):
    """Keep only polygon parts; intersections can leave stray lines and points."""
    if geometry.geom_type in ("Polygon", "MultiPolygon"):
        return geometry
    return unary_union([g for g in getattr(geometry, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")])


def _tag(properties, entry):
    properties.update(entry["set"])
    properties["OVERRIDE"] = entry["id"]
    properties["NOTE"] = entry["note"]
    properties["SOURCES"] = entry["sources"]


def apply(entries, year, geojson, file_for_year):
    """Apply the entries for `year` to `geojson` in place. `file_for_year(y)` returns the path of snapshot y."""
    features = geojson["features"]
    for entry in (e for e in entries if e["year"] == year):
        op = entry["op"]
        if op == "rename":
            point = Point(entry["match"]["point"])
            matches = [
                f for f in features
                if f["properties"].get("NAME") == entry["match"]["name"] and f["geometry"] and _geometry(f).covers(point)
            ]
            if len(matches) != 1:
                raise ValueError(f"{entry['id']}: expected 1 match, found {len(matches)}")
            _tag(matches[0]["properties"], entry)

        elif op == "carve":
            region = _territory(file_for_year(entry["shape_from"]["year"]), entry["shape_from"]["name"])
            hosts = [f for f in features if f["properties"].get("NAME") in entry["hosts"] and f["geometry"]]
            carved = []
            for host in hosts:
                geometry = _geometry(host)
                if not geometry.intersects(region):
                    continue
                piece = _polygonal(geometry.intersection(region))
                if piece.area < MIN_AREA:
                    continue
                carved.append(piece)
                host["geometry"] = mapping(_polygonal(geometry.difference(region)))
            if not carved:
                raise ValueError(f"{entry['id']}: nothing to carve")
            properties = {"BORDERPRECISION": 1}
            _tag(properties, entry)
            features.append({"type": "Feature", "properties": properties, "geometry": mapping(unary_union(carved))})

        elif op == "copy":
            source = json.loads(file_for_year(entry["shape_from"]["year"]).read_text(encoding="utf-8"))["features"]
            matches = [
                f for f in source
                if f["properties"].get("NAME") == entry["shape_from"]["name"] and "CARRIED" not in f["properties"]
            ]
            if len(matches) != 1:
                raise ValueError(f"{entry['id']}: expected 1 source feature, found {len(matches)}")
            properties = dict(matches[0]["properties"])
            _tag(properties, entry)
            features.append({"type": "Feature", "properties": properties, "geometry": matches[0]["geometry"]})

        else:
            raise ValueError(f"{entry['id']}: unknown op {op!r}")
