"""Report data-quality problems in data/entries/ and write docs/data-quality.md.

Run from the repository root:  python pipeline/quality_report.py
Nothing is changed or deleted: every finding is a to-do for a human, listed with the record's
file so a contributor can open it, check a source and fix it in a pull request.
Checks: possible duplicates, coordinates that look wrong, low-precision dates, outliers
(lifespans, dates, thin sources and summaries). Output is deterministic, so re-running on
unchanged data rewrites an identical file.
"""

import collections
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
OUT = ROOT / "docs" / "data-quality.md"

PEOPLE = {"philosopher", "scientist", "writer", "ruler"}
MAX_LIFESPAN = 105
SAME_PLACE_KM = 300
LOW_PRECISION = {"century", "decade", "circa"}


def fold(text: str) -> str:
    """Lowercase, no accents, letters and digits only: 'Aesop' and 'aesop' compare equal."""
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def km(a: dict, b: dict) -> float:
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dlon = math.radians(b["lon"] - a["lon"])
    cos = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dlon)
    return 6371 * math.acos(max(-1.0, min(1.0, cos)))


def year(y: int) -> str:
    return f"{-y} BCE" if y < 0 else f"{y} CE"


def span(r: dict) -> str:
    return year(r["start"]) + (f" to {year(r['end'])}" if "end" in r else "")


def link(r: dict) -> str:
    return f"[`{r['id']}`](../data/entries/{r['id']}.json)"


def load() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ENTRIES.glob("*.json"))]


def find_duplicates(records):
    groups = collections.defaultdict(list)
    for r in records:
        groups[(fold(r["name"]), r["category"])].append(r)
    out = [(rs, "same name and category") for rs in groups.values() if len(rs) > 1]
    # same person under different names: same birth year and category, one name inside the other
    by_start = collections.defaultdict(list)
    for r in records:
        if r["category"] in PEOPLE:
            by_start[(r["start"], r["category"])].append(r)
    seen = {tuple(sorted(x["id"] for x in rs)) for rs, _ in out}
    for rs in by_start.values():
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                fa, fb = fold(a["name"]), fold(b["name"])
                if fa != fb and (fa in fb or fb in fa) and len(min(fa, fb, key=len)) >= 5:
                    key = tuple(sorted((a["id"], b["id"])))
                    if key not in seen:
                        seen.add(key)
                        out.append(([a, b], "same start year, one name inside the other"))
    return out


def find_coordinate_problems(records):
    out = []
    by_place = collections.defaultdict(list)
    for r in records:
        loc = r["location"]
        if loc["lat"] == 0 and loc["lon"] == 0:
            out.append((r, "coordinates are 0, 0"))
        by_place[fold(loc["place"])].append(r)
    for rs in by_place.values():
        if len(rs) < 2:
            continue
        # the most common coordinate pair stands for the place; far-away records are suspect
        pairs = collections.Counter((r["location"]["lat"], r["location"]["lon"]) for r in rs)
        lat, lon = sorted(pairs.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        for r in rs:
            d = km(r["location"], {"lat": lat, "lon": lon})
            if d > SAME_PLACE_KM:
                out.append((r, f"place '{r['location']['place']}' is {d:.0f} km from where other records put it"))
    return out


def find_outliers(records):
    out = []
    for r in records:
        cat = r["category"]
        if cat in PEOPLE and "end" in r and not r.get("disputed"):
            life = r["end"] - r["start"]
            if life > MAX_LIFESPAN:
                out.append((r, "lifespan over 105 years"))
            elif life == 0 and r["date_precision"] not in LOW_PRECISION:
                out.append((r, "birth and death in the same year"))
        if cat in PEOPLE and "end" not in r and r["start"] < 1900:
            out.append((r, "person with no end year"))
        if cat == "work" and "end" in r and r["end"] - r["start"] > 100:
            out.append((r, "work spanning over 100 years"))
        if len(r["summary"]) < 40:
            out.append((r, "very short summary (under 40 characters)"))
        if len(r["sources"]) < 2 and not r.get("disputed"):
            out.append((r, "only one source"))
        if "wikipedia" not in r.get("links", {}):
            out.append((r, "no Wikipedia link"))
    return out


def precision_rows(records):
    rows = []
    for c in sorted({r["category"] for r in records}):
        rs = [r for r in records if r["category"] == c]
        low = sum(r["date_precision"] in LOW_PRECISION for r in rs)
        rows.append(f"| {c} | {len(rs)} | {low} | {100 * low / len(rs):.0f}% |")
    return rows


def render(records) -> str:
    dups = find_duplicates(records)
    coords = find_coordinate_problems(records)
    outliers = find_outliers(records)
    low = [r for r in records if r["date_precision"] in LOW_PRECISION]
    by_reason = collections.defaultdict(list)
    for r, why in outliers:
        by_reason[why].append(r)

    lines = [
        "# Data quality report",
        "",
        "Generated by `python pipeline/quality_report.py`. Do not edit by hand; re-run after data changes.",
        "Findings are **flags for review, not errors**: a long lifespan can be right, and two records with",
        "one name can be two people. Nothing is deleted automatically. To fix one, open the record,",
        "check a source, and send a pull request (see [CONTRIBUTING.md](../CONTRIBUTING.md)).",
        "",
        f"Records checked: **{len(records)}**.",
        "",
        "| Check | Flags |",
        "|---|---:|",
        f"| Possible duplicates | {len(dups)} |",
        f"| Suspicious coordinates | {len(coords)} |",
        f"| Low-precision dates (century, decade, circa) | {len(low)} |",
        f"| Outliers and thin records | {len(outliers)} |",
        "",
        "## Possible duplicates",
        "",
    ]
    lines += [f"- {', '.join(f'{link(r)} ({span(r)})' for r in rs)}: {why}"
              for rs, why in sorted(dups, key=lambda d: d[0][0]["id"])] or ["None found."]
    lines += ["", "## Suspicious coordinates", ""]
    lines += [f"- {link(r)}: {why}" for r, why in sorted(coords, key=lambda c: c[0]["id"])] or ["None found."]
    lines += ["", "## Date precision", "", "| Category | Records | Low precision | Share |", "|---|---:|---:|---:|"]
    lines += precision_rows(records)
    lines += ["", "Records a contributor with a good source could pin to an exact year:", ""]
    lines += [f"- {link(r)}: {span(r)} ({r['date_precision']})" for r in sorted(low, key=lambda r: r["id"])]
    lines += ["", "## Outliers and thin records", ""]
    for why in sorted(by_reason):
        rs = sorted(by_reason[why], key=lambda r: r["id"])
        lines += [f"### {why[0].upper() + why[1:]} ({len(rs)})", ""]
        lines += [f"- {link(r)}: {span(r)}" for r in rs]
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    records = load()
    OUT.write_text(render(records), encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)} for {len(records)} records")


if __name__ == "__main__":
    main()
