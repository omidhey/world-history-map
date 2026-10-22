"""Merge data/entries/*.json into one file for the web page: site/data/entries.json.

Run from the repository root:  python pipeline/build.py
pipeline/build_site.py calls this too, so run_site.bat and the Pages workflow pick it up.
Run pipeline/validate.py first; this script trusts that the records are valid.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
OUT = ROOT / "site" / "data" / "entries.json"

# Only what the map needs; the page links back to the full record on GitHub.
FIELDS = ["id", "name", "category", "start", "end", "date_precision", "location", "summary", "links", "disputed"]


def build_entries() -> int:
    entries = []
    for path in sorted(ENTRIES.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        entries.append({key: record[key] for key in FIELDS if key in record})
    entries.sort(key=lambda e: (e["start"], e["id"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(entries)


if __name__ == "__main__":
    print(f"Wrote {build_entries()} entries to {OUT}")
