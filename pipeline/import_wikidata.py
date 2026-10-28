"""Import philosophers from Wikidata as new records in data/entries/.

Run from the repository root:  python pipeline/import_wikidata.py [--dry-run] [--refresh]

Steps:
  1. Ask the Wikidata query service for humans with occupation philosopher (Q4964182) that have
     a birth date, a birthplace with coordinates and at least MIN_SITELINKS sitelinks.
  2. Read their birth and death dates from the entity data itself (wbgetentities), not from the
     query service. The query service turns years into astronomical numbering (Socrates' birth
     comes back as -0469, not -470) and converts Julian dates to Gregorian (Cicero, born
     3 January 106 BCE, comes back in 107 BCE). The entity data keeps the year as entered, with
     no year 0, like our records. Two known dates (Socrates, Confucius) are checked before
     anything is written.
  3. Write one record per new Wikidata item. Items that already have a record are never touched;
     differences between their dates and Wikidata's are printed for a human to judge.

Both answers are cached in raw/wikidata/; --refresh asks again.
The new files go through the usual review: commit them on a branch and open a pull request.
Facts from Wikidata are CC0. The summaries are a template built from those facts and say that a
summary in our own words is still to be written.
"""

import argparse
import datetime
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
CACHE = ROOT / "raw" / "wikidata"

ENDPOINT = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "world-history-map/0.1 (https://github.com/omidhey/world-history-map; semifact@gmail.com)"
MIN_SITELINKS = 80

# Labels: English, else "mul" (the language-neutral label Wikidata uses for many names since 2024).
QUERY = """
SELECT ?item ?label ?mulLabel ?description ?sitelinks ?article ?place ?placeLabel ?placeMulLabel ?coord
WHERE {
  ?item wdt:P106 wd:Q4964182; wikibase:sitelinks ?sitelinks.
  FILTER(?sitelinks >= %(min_sitelinks)d)
  ?item wdt:P31 wd:Q5; wdt:P569 ?birth.
  ?item wdt:P19 ?place. ?place wdt:P625 ?coord.
  OPTIONAL { ?item rdfs:label ?label. FILTER(LANG(?label) = "en") }
  OPTIONAL { ?item rdfs:label ?mulLabel. FILTER(LANG(?mulLabel) = "mul") }
  OPTIONAL { ?item schema:description ?description. FILTER(LANG(?description) = "en") }
  OPTIONAL { ?place rdfs:label ?placeLabel. FILTER(LANG(?placeLabel) = "en") }
  OPTIONAL { ?place rdfs:label ?placeMulLabel. FILTER(LANG(?placeMulLabel) = "mul") }
  OPTIONAL { ?article schema:about ?item; schema:isPartOf <https://en.wikipedia.org/>. }
}
"""

RANK = {"preferred": 2, "normal": 1}  # deprecated statements are ignored

# Wikidata precision -> our date_precision. 11 = day, 10 = month, 9 = year, 8 = decade, 7 = century.
PRECISION = {11: "day", 10: "year", 9: "year", 8: "decade"}
PRECISION_ORDER = ["day", "year", "circa", "decade", "century"]

# The two known dates checked before writing (see docs/schema.md, "Years").
KNOWN = {
    "Q913": {"start": [-470], "end": [-399]},  # Socrates, 470-399 BCE
    "Q4604": {"start": [-551], "end": [-479]},  # Confucius, 551-479 BCE (Wikidata also has 552)
}


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def cached(name: str, refresh: bool, download):
    path = CACHE / name
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    data = download()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def query(min_sitelinks: int) -> list[dict]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": QUERY % {"min_sitelinks": min_sitelinks}})
    rows = get_json(url)["results"]["bindings"]
    return [{key: value["value"] for key, value in row.items()} for row in rows]


def entities(qids: list[str], props: str) -> dict[str, dict]:
    """wbgetentities, 50 items per request (the API's limit)."""
    found = {}
    for i in range(0, len(qids), 50):
        params = {"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": props, "format": "json"}
        found.update(get_json(API + "?" + urllib.parse.urlencode(params))["entities"])
    return found


def dates(claims: dict, prop: str) -> dict[str, tuple]:
    """Statement id -> (year, precision, rank) for a date property. Years are read as entered."""
    found = {}
    for statement in claims.get(prop, []):
        value = statement["mainsnak"].get("datavalue", {}).get("value")
        if statement["rank"] not in RANK or not value:  # deprecated, or "unknown value"
            continue
        year = int(re.match(r"^([+-]?\d+)-", value["time"]).group(1))
        found[statement["id"]] = (year, PRECISION.get(value["precision"], "century"), RANK[statement["rank"]])
    return found


def best_values(statements: dict[str, tuple]) -> list[tuple[int, str]]:
    """(year, precision) of the best-ranked statements, one per year, the most likely first:
    the year most statements give, then the more precise, then the earlier one."""
    if not statements:
        return []
    top = max(rank for _, _, rank in statements.values())
    best = [(year, precision) for year, precision, rank in statements.values() if rank == top]
    votes = Counter(year for year, _ in best)
    best.sort(key=lambda v: (-votes[v[0]], PRECISION_ORDER.index(v[1]), v[0]))
    seen, values = set(), []
    for year, precision in best:
        if year not in seen:
            seen.add(year)
            values.append((year, precision))
    return values


def group(rows: list[dict], claims: dict[str, dict], place_labels: dict[str, str]) -> dict[str, dict]:
    """One item per Wikidata ID; the query returns one row per place x label combination."""
    items: dict[str, dict] = {}
    for row in rows:
        qid = row["item"].rsplit("/", 1)[1]
        item = items.setdefault(qid, {
            "qid": qid, "label": row.get("label") or row.get("mulLabel"), "description": row.get("description"),
            "sitelinks": int(row["sitelinks"]), "article": row.get("article"),
            "births": dates(claims[qid], "P569"), "deaths": dates(claims[qid], "P570"), "places": {},
        })
        place_qid = row["place"].rsplit("/", 1)[1]
        label = row.get("placeLabel") or row.get("placeMulLabel") or place_labels.get(place_qid) or place_qid
        match = re.match(r"^Point\(([-\d.eE]+) ([-\d.eE]+)\)$", row["coord"])
        if match:  # coordinates on other globes (none expected) are left out
            item["places"].setdefault(place_qid, (label, float(match.group(2)), float(match.group(1))))
    return items


def any_label(entity: dict) -> str | None:
    labels = entity.get("labels", {})
    for language in ("en", "mul", *sorted(labels)):
        if language in labels:
            return labels[language]["value"]
    return None


def load(min_sitelinks: int, refresh: bool) -> dict[str, dict]:
    rows = cached("philosophers.json", refresh, lambda: query(min_sitelinks))
    qids = sorted({row["item"].rsplit("/", 1)[1] for row in rows})
    claims = cached("claims.json", refresh, lambda: {
        qid: {prop: entity["claims"].get(prop, []) for prop in ("P569", "P570")}
        for qid, entity in entities(qids, "claims").items()})
    unnamed = sorted({row["place"].rsplit("/", 1)[1] for row in rows
                      if not row.get("placeLabel") and not row.get("placeMulLabel")})
    place_labels = cached("place_labels.json", refresh, lambda: {
        qid: any_label(entity) for qid, entity in entities(unnamed, "labels").items()})
    return group(rows, claims, place_labels)


def years(item: dict) -> dict[str, list[tuple[int, str]]]:
    return {"start": best_values(item["births"]), "end": best_values(item["deaths"])}


def self_check(items: dict[str, dict]) -> list[str]:
    problems = []
    for qid, expected in KNOWN.items():
        if qid not in items:
            problems.append(f"{qid} is missing from the query result")
            continue
        found = years(items[qid])
        for field, wanted in expected.items():
            got = sorted({year for year, _ in found[field]})
            if not set(wanted) <= set(got):
                problems.append(f"{qid} {field}: expected {wanted}, got {got}")
    return problems


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")[:70].strip("-")


def year_tag(year: int) -> str:
    return f"{-year}-bce" if year < 0 else str(year)


def pick(values: list[tuple[int, str]]) -> tuple[int, str]:
    """The most likely value (best_values puts it first)."""
    return values[0]


def build_record(item: dict, record_id: str) -> dict:
    found = years(item)
    start, start_precision = pick(found["start"])
    precisions = [start_precision]
    end = None
    if found["end"]:
        end, end_precision = pick(found["end"])
        precisions.append(end_precision)
    place, lat, lon = item["places"][min(item["places"])]

    description = (item["description"] or "philosopher").strip()
    summary = f"{description[0].upper()}{description[1:]}, born in {place}. " \
              "Imported from Wikidata; a summary in our own words is still to be written."
    wikidata_url = f"https://www.wikidata.org/wiki/{item['qid']}"

    record = {
        "id": record_id,
        "wikidata": item["qid"],
        "name": item["label"],
        "category": "philosopher",
        "start": start,
    }
    if end is not None:
        record["end"] = end
    record["date_precision"] = max(precisions, key=PRECISION_ORDER.index)
    record["location"] = {"lat": round(lat, 2), "lon": round(lon, 2), "place": place}
    record["summary"] = summary[:400]
    if item["article"]:
        record["links"] = {"wikipedia": item["article"]}
    record["sources"] = [wikidata_url] + ([item["article"]] if item["article"] else [])

    claims = []
    for field, label in (("start", "birth"), ("end", "death")):
        distinct = sorted({year for year, _ in found[field]})
        if len(distinct) > 1:
            claims += [{"field": field, "value": year, "note": f"Wikidata lists more than one {label} year.",
                        "sources": [wikidata_url]} for year in distinct]
    record["disputed"] = bool(claims)
    if claims:
        record["claims"] = claims
    return record


def skip_reason(item: dict) -> str | None:
    if not item["label"] or re.fullmatch(r"Q\d+", item["label"]):
        return "no English label"
    if not item["places"]:
        return "no birthplace on Earth"
    found = years(item)
    if not found["start"]:
        return "no birth year"
    this_year = datetime.date.today().year
    all_years = [year for year, _ in found["start"] + found["end"]]
    if any(year == 0 or year > this_year for year in all_years):
        return "year 0 or a future year"
    if found["end"] and pick(found["start"])[0] > pick(found["end"])[0]:
        return "death before birth"
    return None


def region(lat: float, lon: float) -> str:
    """Rough band, only to make the regional balance of an import visible."""
    if lon < -30:
        return "Americas"
    if lat > 35 and lon < 45:
        return "Europe"
    if lon < 60 and lat > 12:
        return "Middle East / N. Africa" if lat < 42 else "Europe"
    if lon < 52:
        return "Africa"
    if lat < -10 and lon > 110:
        return "Oceania"
    return "Asia"


def existing_records() -> dict[str, dict]:
    return {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in ENTRIES.glob("*.json")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="print the report, write nothing")
    parser.add_argument("--refresh", action="store_true", help="ask Wikidata again instead of using the cache")
    parser.add_argument("--min-sitelinks", type=int, default=MIN_SITELINKS)
    args = parser.parse_args()

    items = load(args.min_sitelinks, args.refresh)
    items = {qid: item for qid, item in items.items() if item["sitelinks"] >= args.min_sitelinks}
    print(f"Wikidata: {len(items)} philosophers with >= {args.min_sitelinks} sitelinks")

    problems = self_check(items)
    if problems:
        print("Date self-check FAILED, nothing written:")
        for problem in problems:
            print("  " + problem)
        return 1
    print("Date self-check passed: Socrates 470-399 BCE, Confucius 551-479 BCE")

    existing = existing_records()
    by_qid = {record["wikidata"]: record for record in existing.values() if "wikidata" in record}
    taken = set(existing)
    written, skipped, differences = [], [], []

    for item in sorted(items.values(), key=lambda i: (-i["sitelinks"], i["qid"])):
        if item["qid"] in by_qid:
            record = by_qid[item["qid"]]
            found = years(item)
            for field in ("start", "end"):
                theirs = sorted({year for year, _ in found[field]})
                if field in record and theirs and record[field] not in theirs:
                    differences.append(f"{record['id']} {field}: ours {record[field]}, Wikidata {theirs}")
            continue
        reason = skip_reason(item)
        if reason:
            skipped.append(f"{item['qid']} {item['label'] or ''}: {reason}")
            continue
        base = slug(item["label"]) or item["qid"].lower()
        start = pick(years(item)["start"])[0]
        for candidate in (base, f"{base}-{year_tag(start)}", f"{base}-{item['qid'].lower()}"):
            if candidate not in taken:
                break
        taken.add(candidate)
        record = build_record(item, candidate)
        written.append(record)
        if not args.dry_run:
            path = ENTRIES / f"{candidate}.json"
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{'Would write' if args.dry_run else 'Wrote'} {len(written)} new records, "
          f"{len(items) - len(written) - len(skipped)} already had a record, skipped {len(skipped)}")
    print(f"Disputed (Wikidata lists more than one year): {sum(r['disputed'] for r in written)}")
    renamed = [r["id"] for r in written if r["id"] != slug(r["name"])]
    if renamed:
        print("Ids changed to avoid a clash: " + ", ".join(renamed))
    for line in skipped:
        print("  skipped " + line)
    print("Existing records whose dates differ from Wikidata (not changed):")
    for line in differences or ["  none"]:
        print("  " + line)

    centuries: dict[str, int] = defaultdict(int)
    for record in sorted(written, key=lambda r: r["start"]):
        start = record["start"]
        centuries[f"{(-start - 1) // 100 + 1}c BCE" if start < 0 else f"{(start - 1) // 100 + 1}c"] += 1
    print("By birth century: " + ", ".join(f"{c} {n}" for c, n in centuries.items()))
    regions = Counter(region(r["location"]["lat"], r["location"]["lon"]) for r in written)
    print("By birthplace region: " + ", ".join(f"{name} {n}" for name, n in regions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
