"""Carry the last recorded realm forward into land the source leaves unnamed.

Project rule: inhabited land that was once held by a realm is never shown as uncoloured again.
Where a snapshot has unnamed land that a realm held in the previous snapshot (after that snapshot's own
carry-forward), the unnamed land is split and the pieces get the previous holder. These pieces are
marked CARRIED = the year the holder was last recorded there by the source, so the map can show them as
an inference, not as source data.

Antarctica (south of 60° S) has no permanent population and is left alone.
Called by download_borders.py after overrides. Needs shapely.
"""

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

MIN_AREA = 0.05  # square degrees (~600 km²); smaller pieces are slivers from differing simplifications
INHABITED = box(-180, -60, 180, 90)
KEEP = ("NAME", "ABBREVN", "SUBJECTO", "PARTOF", "type", "weblnks")


def _geometry(feature):
    return shape(feature["geometry"]).buffer(0) if feature["geometry"] else None


def _polygonal(geometry):
    if geometry.geom_type in ("Polygon", "MultiPolygon"):
        return geometry
    return unary_union([g for g in getattr(geometry, "geoms", []) if g.geom_type in ("Polygon", "MultiPolygon")])


def apply(previous, previous_year, geojson):
    """Fill unnamed land in `geojson` (in place) from the named features of `previous`. Returns area filled."""
    holders = [(f, _geometry(f)) for f in previous["features"] if f["properties"].get("NAME") and f["geometry"]]
    tree = STRtree([g for _, g in holders])

    pieces = {}  # (NAME, SUBJECTO, last recorded year) -> (properties, [geometries])
    filled_area = 0.0
    for feature in geojson["features"]:
        if feature["properties"].get("NAME") or not feature["geometry"]:
            continue
        remaining = _geometry(feature)
        for index in tree.query(remaining.intersection(INHABITED)):
            source, geometry = holders[index]
            piece = _polygonal(remaining.intersection(geometry).intersection(INHABITED))
            if piece.is_empty or piece.area < MIN_AREA:
                continue
            properties = source["properties"]
            last_seen = properties.get("CARRIED", previous_year)
            key = (properties["NAME"], properties.get("SUBJECTO"), last_seen)
            if key not in pieces:
                kept = {k: properties[k] for k in KEEP if k in properties}
                kept.update({"BORDERPRECISION": 1, "CARRIED": last_seen})
                pieces[key] = (kept, [])
            pieces[key][1].append(piece)
            remaining = _polygonal(remaining.difference(piece))
            filled_area += piece.area
        feature["geometry"] = mapping(remaining) if not remaining.is_empty else None

    for properties, geometries in pieces.values():
        geojson["features"].append({"type": "Feature", "properties": properties, "geometry": mapping(unary_union(geometries))})
    return filled_area
