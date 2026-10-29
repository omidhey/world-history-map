"""Download the modern country outlines (Natural Earth Admin-0, 1:110m, public domain).

Writes raw/countries/ne_110m_admin_0_countries.geojson (skipped if already there). Used by
make_lineage.py. Run from the repository root:  .venv/Scripts/python pipeline/download_countries.py
"""

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "raw" / "countries" / "ne_110m_admin_0_countries.geojson"

# Pinned to a commit so re-running gives the same data. Update deliberately.
UPSTREAM_COMMIT = "ca96624a56bd078437bca8184e78163e5039ad19"
URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
    f"{UPSTREAM_COMMIT}/geojson/ne_110m_admin_0_countries.geojson"
)


def main() -> None:
    if TARGET.exists():
        print(f"Already downloaded: {TARGET}")
        return
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    print(f"downloading {URL}")
    with urllib.request.urlopen(URL, timeout=120) as response:
        TARGET.write_bytes(response.read())
    print(f"Wrote {TARGET} ({TARGET.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
