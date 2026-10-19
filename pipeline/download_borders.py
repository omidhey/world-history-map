"""Download and simplify the historical-basemaps border snapshots.

Steps, repeatable at any time:
  1. Download each snapshot in YEARS into raw/borders/ (skipped if already there).
  2. Simplify it with mapshaper (10%, keep-shapes) into data/borders/world_<year>.geojson.
  3. Write data/borders/manifest.json and print before/after sizes.

Run from the repository root:  python pipeline/download_borders.py
Needs Node.js and `npm install` (installs mapshaper locally).
"""

import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw" / "borders"
OUT_DIR = ROOT / "data" / "borders"

# Years are integers, negative = BCE, no year 0 (same convention as historical-basemaps).
YEARS = [-3000, -2000, -1000, -500, -323, -1, 400, 800, 1200, 1500, 1800, 1914, 1945, 2010]

# Pinned to a commit so re-running gives the same data. Update deliberately.
UPSTREAM_COMMIT = "da7a4b735ecef70aebdc9c73e409d8a2500d50f3"
BASE_URL = f"https://raw.githubusercontent.com/aourednik/historical-basemaps/{UPSTREAM_COMMIT}/geojson/"

SIMPLIFY = "10%"


def upstream_name(year: int) -> str:
    """historical-basemaps names BCE files world_bc<N>.geojson."""
    return f"world_bc{-year}.geojson" if year < 0 else f"world_{year}.geojson"


def our_name(year: int) -> str:
    """Our names keep the sign, so they sort and read like the year itself."""
    return f"world_{year}.geojson"


def download(year: int) -> Path:
    target = RAW_DIR / upstream_name(year)
    if target.exists():
        return target
    url = BASE_URL + upstream_name(year)
    print(f"  downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as response:
        target.write_bytes(response.read())
    return target


def find_mapshaper() -> list[str]:
    local = ROOT / "node_modules" / ".bin" / ("mapshaper.cmd" if sys.platform == "win32" else "mapshaper")
    if local.exists():
        return [str(local)]
    npx = shutil.which("npx")
    if npx is None:
        sys.exit("mapshaper not found. Install Node.js, then run `npm install` in the repository root.")
    return [npx, "--no-install", "mapshaper"]


def simplify(mapshaper: list[str], source: Path, target: Path) -> None:
    subprocess.run(
        mapshaper + [str(source), "-simplify", SIMPLIFY, "keep-shapes", "-o", "precision=0.0001", str(target)],
        check=True,
        capture_output=True,
    )


def feature_count(path: Path) -> int:
    return len(json.loads(path.read_text(encoding="utf-8"))["features"])


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mapshaper = find_mapshaper()

    snapshots = []
    print(f"{'year':>6} {'raw KB':>8} {'out KB':>8} {'features':>8}")
    for year in YEARS:
        raw = download(year)
        out = OUT_DIR / our_name(year)
        simplify(mapshaper, raw, out)
        raw_kb = raw.stat().st_size // 1024
        out_kb = out.stat().st_size // 1024
        count = feature_count(out)
        print(f"{year:>6} {raw_kb:>8} {out_kb:>8} {count:>8}")
        snapshots.append({"year": year, "file": our_name(year), "features": count, "raw_kb": raw_kb, "kb": out_kb})

    manifest = {
        "source": "https://github.com/aourednik/historical-basemaps",
        "license": "GPL-3.0",
        "simplify": SIMPLIFY,
        "snapshots": snapshots,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'manifest.json'} ({len(snapshots)} snapshots)")


if __name__ == "__main__":
    main()
