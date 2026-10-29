"""Write data/dynasties/<id>.json and data/rulers/<id>.json from pipeline/rulers_seed.py.

The seed holds what a person decides (which rulers, their reigns, summaries). This script adds
the Wikidata item (looked up from the English Wikipedia article title, cached in raw/), the
links and sources. As a check it compares each reign with the ruler's Wikidata birth and death
years and prints what looks odd. Existing files are never overwritten.

Run from the repository root:  python pipeline/make_rulers.py [--refresh]
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

from import_wikidata import BIRTH, DEATH, entities, titles_to_qids, year_values
from make_polities import wikipedia_url
from rulers_seed import STATES

ROOT = Path(__file__).resolve().parent.parent
DYNASTIES = ROOT / "data" / "dynasties"
RULERS = ROOT / "data" / "rulers"


def slug(name: str) -> str:
    text = unicodedata.normalize("NFKD", name.replace("Æ", "Ae").replace("æ", "ae"))
    text = text.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def record(base: dict, qid: str | None, title: str, precision: str) -> dict:
    url = wikipedia_url(title)
    out = {"id": base["id"]}
    if qid:
        out["wikidata"] = qid
    out["name"] = base["name"]
    out["polity"] = base["polity"]
    for key in ("title", "dynasty"):
        if base.get(key):
            out[key] = base[key]
    out["start"] = base["start"]
    out["end"] = base["end"]
    out["date_precision"] = precision
    if base.get("summary"):
        out["summary"] = base["summary"]
    out["links"] = {"wikipedia": url}
    out["sources"] = ([f"https://www.wikidata.org/wiki/{qid}"] if qid else []) + [url]
    out["disputed"] = False
    return out


def write_new(folder: Path, base: dict, qid: str | None, title: str, precision: str) -> int:
    path = folder / f"{base['id']}.json"
    if path.exists():
        return 0
    path.write_text(json.dumps(record(base, qid, title, precision), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1


def main() -> int:
    refresh = "--refresh" in sys.argv
    titles = sorted({row[2] for s in STATES for row in s["dynasties"]} | {row[5] for s in STATES for row in s["rulers"]})
    qids = titles_to_qids(titles, "rulers_titles.json", refresh)
    people = entities([q for t in titles if (q := qids.get(t))], "claims")
    DYNASTIES.mkdir(parents=True, exist_ok=True)
    RULERS.mkdir(parents=True, exist_ok=True)
    written, ids, used_qids = 0, set(), set()
    for state in STATES:
        for dyn_id, name, title, start, end, summary in state["dynasties"]:
            assert dyn_id not in ids, dyn_id
            ids.add(dyn_id)
            qid = qids.get(title)
            if not qid:
                print(f"{dyn_id}: no Wikidata item for '{title}'")
            elif qid in used_qids:
                print(f"{dyn_id}: '{title}' is already another record's item {qid}; left without a Wikidata id")
                qid = None
            used_qids.add(qid or "")
            base = dict(id=dyn_id, name=name, polity=state["polity"], start=start, end=end, summary=summary)
            written += write_new(DYNASTIES, base, qid, title, state["precision"])
        for name, rank, dynasty, start, end, title in state["rulers"]:
            rid = slug(name)
            assert rid not in ids, rid
            ids.add(rid)
            qid = qids.get(title)
            if not qid:
                print(f"{rid}: no Wikidata item for '{title}'")
            else:
                if qid in used_qids:
                    print(f"{rid}: '{title}' is already another record's item {qid}; left without a Wikidata id")
                    qid = None
                used_qids.add(qid or "")
            if qid:
                born = [y for y, pr in year_values(people[qid], BIRTH) if pr in ("day", "year")]  # century/decade values are placeholders
                died = [y for y, pr in year_values(people[qid], DEATH) if pr in ("day", "year")]
                if born and start < born[0]:
                    print(f"CHECK {rid}: reign starts {start}, before birth {born[0]}")
                if died and end > died[0] + 1:
                    print(f"CHECK {rid}: reign ends {end}, after death {died[0]}")
            base = dict(id=rid, name=name, polity=state["polity"], title=rank, dynasty=dynasty, start=start, end=end)
            written += write_new(RULERS, base, qid, title, state["precision"])
    print(f"Wrote {written} new record(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
