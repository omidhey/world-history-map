"""Write data/polities/<id>.json from pipeline/polities_seed.json.

The seed holds what a person decides (which border names a state covers, type, dates,
capital, a summary in our own words). This script adds the Wikidata item (looked up from the
English Wikipedia article title, cached in raw/) and the links and sources.
Existing polity files are never overwritten; re-running writes nothing new.

Run from the repository root:  python pipeline/make_polities.py [--refresh]
"""

import json
import sys
import urllib.parse
from pathlib import Path

from import_wikidata import titles_to_qids

ROOT = Path(__file__).resolve().parent.parent
SEED = Path(__file__).resolve().parent / "polities_seed.json"
POLITIES = ROOT / "data" / "polities"


def wikipedia_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe="_(),'-")


def build_record(seed: dict, qid: str | None) -> dict:
    url = wikipedia_url(seed["wikipedia"])
    record = {"id": seed["id"]}
    if qid:
        record["wikidata"] = qid
    record.update(name=seed["name"], border_names=seed["border_names"], type=seed["type"], start=seed["start"])
    if "end" in seed:
        record["end"] = seed["end"]
    record["date_precision"] = seed["date_precision"]
    if "capital" in seed:
        place, lat, lon = seed["capital"]
        record["capital"] = {"lat": lat, "lon": lon, "place": place}
    record["summary"] = seed["summary"]
    record["links"] = {"wikipedia": url}
    record["sources"] = ([f"https://www.wikidata.org/wiki/{qid}"] if qid else []) + [url]
    record["disputed"] = False
    return record


def main() -> int:
    seeds = json.loads(SEED.read_text(encoding="utf-8"))
    qids = titles_to_qids([s["wikipedia"] for s in seeds], "polities_titles.json", "--refresh" in sys.argv)
    POLITIES.mkdir(parents=True, exist_ok=True)
    used: set[str] = set()
    written = 0
    for seed in seeds:
        qid = qids.get(seed["wikipedia"])
        if qid in used:
            print(f"{seed['id']}: {seed['wikipedia']} is already another polity's item {qid}; left without a Wikidata id")
            qid = None
        elif not qid:
            print(f"{seed['id']}: no Wikidata item found for '{seed['wikipedia']}'")
        used.add(qid or "")
        path = POLITIES / f"{seed['id']}.json"
        if path.exists():
            continue
        path.write_text(json.dumps(build_record(seed, qid), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written += 1
    print(f"Wrote {written} new polity record(s); {len(seeds) - written} already existed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
