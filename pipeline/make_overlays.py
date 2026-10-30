"""Cropland overlays from HYDE 3.5 (CC BY 4.0), one PNG per HYDE time step used by a border snapshot.

Reads, from raw/hyde/: general_files/landlake.asc, general_files/garea_cr.asc and the baseline
land-use zips (any *.zip there or in --zips) holding cropland<yr>BC|AD.asc. Writes
data/overlays/cropland_<hydeyear>.png (RGBA, 1080x1080 Web Mercator (+-85.05 deg), alpha = cropland share of the cell) and
data/overlays/manifest.json (border snapshot year -> HYDE year shown). One grid is held in memory
at a time. Run from the repository root:  .venv/Scripts/python pipeline/make_overlays.py [zip ...]
"""

import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "hyde"
OUT = ROOT / "data" / "overlays"
FACTOR = 4  # 4320x2160 -> 1080x540
NAME = re.compile(r"cropland(\d+)(BC|AD)\.asc$", re.IGNORECASE)
GREEN = (46, 125, 50)


def max_gap(year):
    """HYDE's step in that era (1000 y to 0, 100 y to 1700, 10 y to 2000, then 1 y); a snapshot further
    than that from every earlier grid is missing data, not 'the same as before', so it gets no overlay."""
    return 1000 if year <= 0 else 100 if year <= 1700 else 10 if year <= 2000 else 1



def read_grid(handle):
    for _ in range(6):
        handle.readline()
    return np.loadtxt(handle, dtype=np.float32)


def hyde_year(match):
    n = int(match.group(1))
    return -n if match.group(2).upper() == "BC" else n


def find_entries(zips):
    entries = {}
    for path in zips:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                m = NAME.search(name)
                if m:
                    entries[hyde_year(m)] = (path, name)
    return entries


def block_mean(a):
    h, w = a.shape
    return a.reshape(h // FACTOR, FACTOR, w // FACTOR, FACTOR).mean(axis=(1, 3))


MERC_LAT = 85.0511287798  # Leaflet's Web Mercator limit

def to_mercator(share):
    """Resample equirectangular rows (linear in latitude) to Web Mercator rows, which is how Leaflet
    stretches an image between its bounds. Without this the layer drifts from the map when zooming."""
    h, w = share.shape
    out_h = w  # Mercator world is square
    y = (np.arange(out_h) + 0.5) / out_h
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1 - 2 * y)))) 
    src = np.clip((90 - lat) / 180 * h - 0.5, 0, h - 1)
    lo = np.floor(src).astype(int)
    hi = np.minimum(lo + 1, h - 1)
    t = (src - lo)[:, None]
    return share[lo] * (1 - t) + share[hi] * t


def main():
    zips = [Path(p) for p in sys.argv[1:]] or sorted(RAW.glob("*.zip"))
    entries = find_entries(zips)
    if not entries:
        sys.exit("No cropland<yr>BC|AD.asc files found in " + ", ".join(map(str, zips)) + ". Put the HYDE land-use zips in raw/hyde/.")
    snapshots = [s["year"] for s in json.loads((ROOT / "data" / "borders" / "manifest.json").read_text(encoding="utf-8"))["snapshots"]]
    available = sorted(entries)
    used = {}
    for year in snapshots:
        at_or_before = [y for y in available if year - max_gap(year) <= y <= year]
        if at_or_before:
            used[year] = max(at_or_before)

    with open(RAW / "general_files" / "landlake.asc") as f:
        land = read_grid(f) == 1
    with open(RAW / "general_files" / "garea_cr.asc") as f:
        area = read_grid(f)
    land_cells = block_mean(land.astype(np.float32))
    OUT.mkdir(parents=True, exist_ok=True)
    for hy in sorted(set(used.values())):
        zip_path, name = entries[hy]
        with zipfile.ZipFile(zip_path) as z, z.open(name) as raw:
            import io
            crop = read_grid(io.TextIOWrapper(raw))
        share = np.where((area > 0) & (crop >= 0), crop / np.where(area > 0, area, 1), 0)
        share = np.clip(block_mean(share.astype(np.float32)), 0, 1) * (land_cells > 0.5)
        share = to_mercator(share)
        rgba = np.zeros(share.shape + (4,), dtype=np.uint8)
        rgba[..., :3] = GREEN
        rgba[..., 3] = np.round(np.sqrt(share) * 230).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(OUT / f"cropland_{hy}.png", optimize=True)
        print(f"{hy}: max share {share.max():.2f}, {(OUT / f'cropland_{hy}.png').stat().st_size // 1024} KB")
    manifest = {"source": "HYDE 3.5 baseline, cropland share of cell; downsampled 4x", "license": "CC BY 4.0",
                "bounds": [[-MERC_LAT, -180], [MERC_LAT, 180]],
                "snapshots": {str(k): v for k, v in used.items()}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Snapshots without a HYDE step at or before them are left out:", [y for y in snapshots if y not in used])


if __name__ == "__main__":
    main()
