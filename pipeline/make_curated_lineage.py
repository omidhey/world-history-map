"""Curated lineages: clean up the automatic area match for a few countries and attach sources.

Reads data/lineage/<ISO>.json (make_lineage.py) and pipeline/curated_lineage_seed.json, writes
data/lineage_curated/<ISO>.json. Shares stay those of the automatic area match; curation drops
noise (unnamed land, slivers, listed names), merges repeated names, and adds notes and sources.
Run from the repository root:  python pipeline/make_curated_lineage.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "pipeline" / "curated_lineage_seed.json"
OUT = ROOT / "data" / "lineage_curated"
DEFAULT_MIN_SHARE = 0.04


def curate(auto: dict, rules: dict) -> dict:
    min_share = rules.get("min_share", DEFAULT_MIN_SHARE)
    drop = set(rules.get("drop", []))
    snapshots = {}
    for year, entries in auto["snapshots"].items():
        merged: dict[str, dict] = {}
        for e in entries:
            if e.get("other") or not e["name"] or e["name"] in drop:
                continue
            if e["name"] in merged:
                merged[e["name"]]["share"] += e["share"]
            else:
                merged[e["name"]] = {"name": e["name"], "subjecto": e["subjecto"], "share": e["share"]}
        kept = [e for e in merged.values() if e["share"] >= min_share]
        if rules.get("renormalise") and kept:
            # Rescale against everything that is not dropped, so the dropped region leaves no gap.
            total = sum(e["share"] for e in entries if not e.get("other") and e["name"] not in drop) or 1
            for e in kept:
                e["share"] /= total
        kept.sort(key=lambda e: -e["share"])
        for e in kept:
            e["share"] = round(min(e["share"], 1.0), 4)
        snapshots[year] = kept
    return snapshots


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for iso, rules in seed.items():
        if iso.startswith("_"):
            continue
        auto = json.loads((ROOT / "data" / "lineage" / f"{iso}.json").read_text(encoding="utf-8"))
        record = {"country": iso, "name": auto["name"], "area_km2": auto["area_km2"], "source": "curated",
                  "sources": rules["sources"]}
        if "note" in rules:
            record["note"] = rules["note"]
        record["notes"] = rules.get("notes", {})
        record["snapshots"] = curate(auto, rules)
        (OUT / f"{iso}.json").write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{iso}: {sum(len(v) for v in record['snapshots'].values())} entries")


if __name__ == "__main__":
    main()
