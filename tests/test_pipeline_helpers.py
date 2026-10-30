"""Small pure helpers in the pipeline: HYDE year handling and carry-forward of unnamed land."""

import re

import pytest

pytest.importorskip("PIL")
import make_overlays  # noqa: E402


@pytest.mark.parametrize("year,gap", [(-3000, 1000), (0, 1000), (1, 100), (1500, 100), (1700, 100), (1800, 10), (2000, 10), (2010, 1)])
def test_max_gap_follows_hydes_time_steps(year, gap):
    assert make_overlays.max_gap(year) == gap


@pytest.mark.parametrize("name,year", [("cropland1000BC.asc", -1000), ("cropland0AD.asc", 0), ("x/cropland1500AD.asc", 1500)])
def test_hyde_year_signs_bce(name, year):
    assert make_overlays.hyde_year(make_overlays.NAME.search(name)) == year


def test_block_mean_averages_factor_squares():
    np = pytest.importorskip("numpy")
    big = np.ones((make_overlays.FACTOR * 2, make_overlays.FACTOR * 3), dtype=np.float32)
    big[: make_overlays.FACTOR, : make_overlays.FACTOR] = 0
    out = make_overlays.block_mean(big)
    assert out.shape == (2, 3) and out[0, 0] == 0 and out[1, 2] == 1


def test_carry_forward_fills_unnamed_land_with_previous_holder():
    pytest.importorskip("shapely")
    import carry_forward

    def feature(name, ring):
        props = {"NAME": name} if name else {"NAME": None}
        return {"type": "Feature", "properties": props, "geometry": {"type": "Polygon", "coordinates": [ring]}}

    square = [[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]
    previous = {"features": [feature("Rome", square)]}
    current = {"features": [feature(None, square)]}
    filled = carry_forward.apply(previous, -100, current)
    assert filled == pytest.approx(100)
    carried = [f for f in current["features"] if f["properties"].get("CARRIED") == -100]
    assert carried and carried[0]["properties"]["NAME"] == "Rome"
