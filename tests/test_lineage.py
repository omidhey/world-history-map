"""Lineage shares: which share of a country's area each historical state covers (pipeline/make_lineage.py)."""

import pytest

gpd = pytest.importorskip("geopandas")
from shapely.geometry import box  # noqa: E402

import make_lineage  # noqa: E402

CRS = make_lineage.EQUAL_AREA


def countries(*rows):
    frame = gpd.GeoDataFrame({"iso": [r[0] for r in rows], "geometry": [r[1] for r in rows]}, crs=CRS)
    frame["area"] = frame.geometry.area
    return frame


def states(*rows):
    """rows: (NAME, SUBJECTO, CARRIED or None, geometry)"""
    frame = gpd.GeoDataFrame(
        {"NAME": [r[0] for r in rows], "SUBJECTO": [r[1] for r in rows],
         "CARRIED": [-99999 if r[2] is None else r[2] for r in rows], "geometry": [r[3] for r in rows]},
        crs=CRS,
    )
    return frame


COUNTRY = box(0, 0, 100, 100)


def test_half_covered_country():
    result = make_lineage.shares_for_snapshot(countries(("AAA", COUNTRY)), states(("A", "A", None, box(0, 0, 50, 100))))
    assert result["AAA"] == [{"name": "A", "subjecto": "A", "share": 0.5}]


def test_shares_sorted_largest_first():
    result = make_lineage.shares_for_snapshot(
        countries(("AAA", COUNTRY)),
        states(("Small", "S", None, box(0, 0, 20, 100)), ("Big", "B", None, box(20, 0, 100, 100))),
    )
    assert [e["name"] for e in result["AAA"]] == ["Big", "Small"]
    assert [e["share"] for e in result["AAA"]] == [0.8, 0.2]


def test_slivers_are_folded_into_other():
    # B covers 0.5 % of the country, below MIN_SHARE.
    result = make_lineage.shares_for_snapshot(
        countries(("AAA", COUNTRY)),
        states(("A", "A", None, box(0, 0, 50, 100)), ("B", "B", None, box(99.5, 0, 100, 100))),
    )
    names = [e["name"] for e in result["AAA"]]
    assert names == ["A", "other"]
    assert result["AAA"][-1] == {"name": "other", "subjecto": None, "share": 0.005, "other": True}


def test_carried_year_is_passed_through():
    result = make_lineage.shares_for_snapshot(countries(("AAA", COUNTRY)), states(("A", "A", -500, COUNTRY)))
    assert result["AAA"][0]["carried"] == -500


def test_country_with_no_state_gets_empty_list():
    result = make_lineage.shares_for_snapshot(countries(("AAA", COUNTRY)), states(("A", "A", None, box(200, 200, 300, 300))))
    assert result["AAA"] == []


def test_unnamed_land_has_none_name():
    result = make_lineage.shares_for_snapshot(countries(("AAA", COUNTRY)), states(("", "", None, COUNTRY)))
    assert result["AAA"][0]["name"] is None and result["AAA"][0]["subjecto"] is None
