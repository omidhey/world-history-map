"""Merge data/entries/*.json into one file for the web page: site/data/entries.json,
data/polities/*.json into site/data/polities.json, and data/dynasties and data/rulers
into site/data/rulers.json (grouped by polity).

Run from the repository root:  python pipeline/build.py
pipeline/build_site.py calls this too, so run_site.bat and the Pages workflow pick it up.
Run pipeline/validate.py first; this script trusts that the records are valid.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
OUT = ROOT / "site" / "data" / "entries.json"
POLITIES = ROOT / "data" / "polities"
POLITIES_OUT = ROOT / "site" / "data" / "polities.json"
DYNASTIES = ROOT / "data" / "dynasties"
RULERS = ROOT / "data" / "rulers"
RULERS_OUT = ROOT / "site" / "data" / "rulers.json"

# Only what the map needs; the page links back to the full record on GitHub.
FIELDS = ["id", "name", "category", "start", "end", "date_precision", "location", "summary", "links", "sources", "disputed", "claims"]


def build_entries() -> int:
    entries = []
    for path in sorted(ENTRIES.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        entry = {key: record[key] for key in FIELDS if key in record}
        if record.get("claims"):
            # Disputed dates: the page shows the record in every period any claim reaches.
            years = [record["start"], record.get("end", record["start"])]
            years += [claim["value"] for claim in record["claims"]]
            entry["span"] = [min(years), max(years)]
        entries.append(entry)
    entries.sort(key=lambda e: (e["start"], e["id"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(entries)


POLITY_FIELDS = ["id", "name", "type", "start", "end", "date_precision", "capital", "summary", "links", "sources", "disputed", "claims"]


def build_polities() -> int:
    """polities.json: the cards, and which border NAME opens which card (a name can have several, in different eras)."""
    polities, names = [], {}
    for path in sorted(POLITIES.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        polities.append({key: record[key] for key in POLITY_FIELDS if key in record})
        for border_name in record["border_names"]:
            names.setdefault(border_name, []).append(record["id"])

    POLITIES_OUT.parent.mkdir(parents=True, exist_ok=True)
    POLITIES_OUT.write_text(json.dumps({"polities": polities, "names": names}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return len(polities)


DYNASTY_FIELDS = ["id", "name", "start", "end", "date_precision", "summary", "links", "sources", "disputed", "claims"]
RULER_FIELDS = ["id", "name", "title", "dynasty", "start", "end", "date_precision", "links", "sources", "disputed", "claims"]


def build_rulers() -> int:
    """rulers.json: {polity id: {"dynasties": [...], "rulers": [...]}}, each list ordered by start year."""
    out, count = {}, 0
    for folder, key, fields in ((DYNASTIES, "dynasties", DYNASTY_FIELDS), (RULERS, "rulers", RULER_FIELDS)):
        for path in sorted(folder.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            group = out.setdefault(record["polity"], {"dynasties": [], "rulers": []})
            group[key].append({k: record[k] for k in fields if k in record})
            count += 1
    for group in out.values():
        for key in group:
            group[key].sort(key=lambda r: (r["start"], r["id"]))
    RULERS_OUT.parent.mkdir(parents=True, exist_ok=True)
    RULERS_OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return count


if __name__ == "__main__":
    print(f"Wrote {build_entries()} entries to {OUT}")
    print(f"Wrote {build_polities()} polities to {POLITIES_OUT}")
    print(f"Wrote {build_rulers()} dynasties and rulers to {RULERS_OUT}")
