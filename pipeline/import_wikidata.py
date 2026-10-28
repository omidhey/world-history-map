"""Import philosophers from Wikidata as new records in data/entries/.

Run from the repository root:  python pipeline/import_wikidata.py [--dry-run] [--refresh]

Who is imported, aiming at philosophers whose thought is studied rather than whoever is famous:
  1. Humans with occupation philosopher who have an article in the Stanford Encyclopedia of
     Philosophy or the Internet Encyclopedia of Philosophy (as recorded on Wikidata) and at least
     MIN_SITELINKS sitelinks.
  2. Everyone in pipeline/philosophers_canon.json: a curated list per tradition (Chinese, Indian,
     Islamic, African, Latin American...), because both encyclopedias and Wikidata cover thinkers
     outside Europe thinly. Add to it by pull request.

Dates are read from the entity data (wbgetentities), not from the query service. The query
service turns years into astronomical numbering (Socrates' birth comes back as -0469, not -470)
and converts Julian dates to Gregorian (Cicero, born 3 January 106 BCE, comes back in 107 BCE).
The entity data keeps the year as entered, with no year 0, like our records. Two known dates
(Socrates, Confucius) are checked before anything is written. Without a birth date, the floruit
("flourished") date is used.

Location: the birthplace, else where the person worked, else where they died; a place without
coordinates borrows those of the region it lies in (Mencius' birthplace, the state of Zou).

Items that already have a record are never touched; differences between their dates and
Wikidata's are printed for a human to judge. Answers are cached in raw/wikidata/; --refresh asks
again. The new files go through the usual review: commit them on a branch and open a pull request.
Facts from Wikidata are CC0. The summaries are a template built from those facts and say that a
summary in our own words is still to be written.
"""

import argparse
import datetime
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
CANON = Path(__file__).resolve().parent / "philosophers_canon.json"
CACHE = ROOT / "raw" / "wikidata"

ENDPOINT = "https://query.wikidata.org/sparql"
API = "https://www.wikidata.org/w/api.php"
USER_AGENT = "world-history-map/0.1 (https://github.com/omidhey/world-history-map; semifact@gmail.com)"
MIN_SITELINKS = 50

QUERY = """
SELECT DISTINCT ?item WHERE {
  { ?item wdt:P3123 [] } UNION { ?item wdt:P5088 [] }
  ?item wdt:P31 wd:Q5; wikibase:sitelinks ?sitelinks; wdt:P106/wdt:P279* wd:Q4964182.
  FILTER(?sitelinks >= %(min_sitelinks)d)
}
"""

SEP, IEP = "P3123", "P5088"  # Stanford / Internet Encyclopedia of Philosophy article ids
BIRTH, DEATH, FLORUIT = "P569", "P570", "P1317"
PLACES = [("P19", "born in"), ("P937", "worked in"), ("P20", "died in")]  # in order of preference
COORDINATES, LOCATED_IN = "P625", "P131"

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
    for attempt in range(5):
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
        if "error" not in data:
            return data
        time.sleep(5)  # the API answers rate limits with an error object
    raise RuntimeError(f"Wikidata kept answering with an error: {data['error']}")


def cached(name: str, refresh: bool, download):
    path = CACHE / name
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    data = download()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return data


def query(min_sitelinks: int) -> list[str]:
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": QUERY % {"min_sitelinks": min_sitelinks}})
    return sorted(row["item"]["value"].rsplit("/", 1)[1] for row in get_json(url)["results"]["bindings"])


def entities(qids: list[str], props: str) -> dict[str, dict]:
    """wbgetentities, 50 items per request (the API's limit), keeping only what the import uses."""
    keep = {BIRTH, DEATH, FLORUIT, SEP, IEP, COORDINATES, LOCATED_IN, *(p for p, _ in PLACES)}
    found = {}
    for i in range(0, len(qids), 50):
        params = {"action": "wbgetentities", "ids": "|".join(qids[i:i + 50]), "props": props,
                  "languages": "en|mul", "sitefilter": "enwiki", "format": "json"}
        for qid, entity in get_json(API + "?" + urllib.parse.urlencode(params))["entities"].items():
            if "claims" in entity:
                entity["claims"] = {p: s for p, s in entity["claims"].items() if p in keep}
            found[qid] = entity
        time.sleep(0.2)
    return found


def best(entity: dict, prop: str) -> list[dict]:
    """Values of the best-ranked statements (preferred, else normal) of a property."""
    statements = [s for s in entity.get("claims", {}).get(prop, [])
                  if s["rank"] in RANK and s["mainsnak"].get("datavalue")]  # not deprecated, not "unknown value"
    if not statements:
        return []
    top = max(RANK[s["rank"]] for s in statements)
    return [s["mainsnak"]["datavalue"]["value"] for s in statements if RANK[s["rank"]] == top]


def year_values(entity: dict, prop: str) -> list[tuple[int, str]]:
    """(year, precision), one per year, the most likely first: the year most statements give,
    then the more precise, then the earlier one. Years are read as entered (no year 0)."""
    values = [(int(re.match(r"^([+-]?\d+)-", v["time"]).group(1)), PRECISION.get(v["precision"], "century"))
              for v in best(entity, prop)]
    votes = Counter(year for year, _ in values)
    values.sort(key=lambda v: (-votes[v[0]], PRECISION_ORDER.index(v[1]), v[0]))
    seen, distinct = set(), []
    for year, precision in values:
        if year not in seen:
            seen.add(year)
            distinct.append((year, precision))
    return distinct


def label(entity: dict) -> str | None:
    """English label, else "mul" (the language-neutral label Wikidata uses for many names since 2024)."""
    labels = entity.get("labels", {})
    for language in ("en", "mul"):
        if language in labels:
            return labels[language]["value"]
    return None


def load(min_sitelinks: int, refresh: bool) -> tuple[dict[str, dict], dict[str, dict], dict[str, str]]:
    """People, places (with the regions they lie in) and the tradition of each canon entry."""
    canon = {person["qid"]: {**person, "tradition": group["tradition"]}
             for group in json.loads(CANON.read_text(encoding="utf-8")) for person in group["people"]}
    selected = cached("philosophers.json", refresh, lambda: query(min_sitelinks))
    qids = sorted(set(selected) | set(canon) | set(KNOWN))
    people = cached("people.json", refresh, lambda: entities(qids, "labels|descriptions|claims|sitelinks"))

    def place_ids(entities_: dict, props: list[str]) -> list[str]:
        return sorted({v["id"] for e in entities_.values() for p in props for v in best(e, p)})

    places = cached("places.json", refresh, lambda: entities(place_ids(people, [p for p, _ in PLACES]), "labels|claims"))
    regions = cached("regions.json", refresh, lambda: entities(
        place_ids({q: e for q, e in places.items() if not best(e, COORDINATES)}, [LOCATED_IN]), "labels|claims"))
    return people, {**regions, **places}, canon


def location(person: dict, places: dict[str, dict], curated: dict | None) -> tuple[str, float, float, str, str | None] | None:
    """(place name, lat, lon, how it relates to the person, extra source) from the first place with coordinates,
    else the place given in the curated list (only for people Wikidata has no usable place for)."""
    for prop, relation in PLACES:
        for value in best(person, prop):
            place = places.get(value["id"], {})
            candidates = [place] + [places.get(v["id"], {}) for v in best(place, LOCATED_IN)]
            for candidate in candidates:
                coords = [c for c in best(candidate, COORDINATES) if c.get("globe", "").endswith("Q2")]  # Earth
                if coords:
                    return label(place) or value["id"], coords[0]["latitude"], coords[0]["longitude"], relation, None
    if curated and "place" in curated:
        place = curated["place"]
        return place["name"], place["lat"], place["lon"], place["relation"], place["source"]
    return None


def item(qid: str, person: dict, places: dict[str, dict], curated: dict | None) -> dict:
    sitelink = person.get("sitelinks", {}).get("enwiki")
    births = year_values(person, BIRTH)
    floruit = [] if births else year_values(person, FLORUIT)
    return {
        "qid": qid, "label": label(person),
        # The curated list may correct a wrong Wikidata description, with a source.
        "description": (curated or {}).get("description") or person.get("descriptions", {}).get("en", {}).get("value"),
        "description_source": (curated or {}).get("description_source"),
        "article": "https://en.wikipedia.org/wiki/" + sitelink["title"].replace(" ", "_") if sitelink else None,
        "start": births or floruit, "floruit": bool(floruit), "end": year_values(person, DEATH),
        "location": location(person, places, curated), "tradition": curated and curated["tradition"],
        "sep": best(person, SEP), "iep": best(person, IEP),
    }


def self_check(people: dict[str, dict]) -> list[str]:
    problems = []
    for qid, expected in KNOWN.items():
        if qid not in people:
            problems.append(f"{qid} is missing from the Wikidata answer")
            continue
        for field, prop in (("start", BIRTH), ("end", DEATH)):
            got = sorted(year for year, _ in year_values(people[qid], prop))
            if not set(expected[field]) <= set(got):
                problems.append(f"{qid} {field}: expected {expected[field]}, got {got}")
    return problems


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")[:70].strip("-")


def year_tag(year: int) -> str:
    return f"{-year}-bce" if year < 0 else str(year)


def build_record(entry: dict, record_id: str) -> dict:
    start, start_precision = entry["start"][0]
    precisions = [start_precision, "circa"] if entry["floruit"] else [start_precision]
    end = None
    if entry["end"]:
        end, end_precision = entry["end"][0]
        precisions.append(end_precision)
    place, lat, lon, relation, place_source = entry["location"]

    description = (entry["description"] or "philosopher").strip()
    summary = f"{description[0].upper()}{description[1:]}, {relation} {place}. " \
              "Imported from Wikidata; a summary in our own words is still to be written."
    wikidata_url = f"https://www.wikidata.org/wiki/{entry['qid']}"

    record = {
        "id": record_id,
        "wikidata": entry["qid"],
        "name": entry["label"],
        "category": "philosopher",
        "start": start,
    }
    if end is not None:
        record["end"] = end
    record["date_precision"] = max(precisions, key=PRECISION_ORDER.index)
    record["location"] = {"lat": round(lat, 2), "lon": round(lon, 2), "place": place}
    record["summary"] = summary[:400]
    if entry["article"]:
        record["links"] = {"wikipedia": entry["article"]}
    record["sources"] = [wikidata_url] + ([entry["article"]] if entry["article"] else []) \
        + [f"https://plato.stanford.edu/entries/{sep}/" for sep in entry["sep"][:1]] \
        + [f"https://iep.utm.edu/{iep}/" for iep in entry["iep"][:1]]
    for extra in (place_source, entry["description_source"]):
        if extra and extra not in record["sources"]:
            record["sources"].append(extra)

    claims = []
    for field, kind in (("start", "floruit" if entry["floruit"] else "birth"), ("end", "death")):
        distinct = sorted(year for year, _ in entry[field])
        if len(distinct) > 1:
            claims += [{"field": field, "value": year, "note": f"Wikidata lists more than one {kind} year.",
                        "sources": [wikidata_url]} for year in distinct]
    record["disputed"] = bool(claims)
    if claims:
        record["claims"] = claims
    return record


def skip_reason(entry: dict) -> str | None:
    if not entry["label"] or re.fullmatch(r"Q\d+", entry["label"]):
        return "no English label"
    if not entry["location"]:
        return "no place with coordinates (birth, work or death)"
    if not entry["start"]:
        return "no birth or floruit year"
    this_year = datetime.date.today().year
    all_years = [year for year, _ in entry["start"] + entry["end"]]
    if any(year == 0 or year > this_year for year in all_years):
        return "year 0 or a future year"
    if entry["end"] and entry["start"][0][0] > entry["end"][0][0]:
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

    people, places, canon = load(args.min_sitelinks, args.refresh)
    problems = self_check(people)
    if problems:
        print("Date self-check FAILED, nothing written:")
        for problem in problems:
            print("  " + problem)
        return 1
    print("Date self-check passed: Socrates 470-399 BCE, Confucius 551-479 BCE")

    selected = set(cached("philosophers.json", False, lambda: []))
    wanted = sorted(selected | set(canon))
    print(f"Wikidata: {len(selected)} with an encyclopedia article and >= {args.min_sitelinks} sitelinks, "
          f"{len(canon)} in the curated list, {len(wanted)} together")

    existing = existing_records()
    by_qid = {record["wikidata"]: record for record in existing.values() if "wikidata" in record}
    taken = set(existing)
    written, skipped, differences = [], [], []

    for qid in wanted:
        entry = item(qid, people[qid], places, canon.get(qid))
        if qid in by_qid:
            record = by_qid[qid]
            for field in ("start", "end"):
                theirs = sorted(year for year, _ in entry[field])
                if field in record and theirs and record[field] not in theirs:
                    differences.append(f"{record['id']} {field}: ours {record[field]}, Wikidata {theirs}")
            continue
        reason = skip_reason(entry)
        if reason:
            skipped.append(f"{qid} {entry['label'] or ''}: {reason}")
            continue
        base = slug(entry["label"]) or qid.lower()
        for candidate in (base, f"{base}-{year_tag(entry['start'][0][0])}", f"{base}-{qid.lower()}"):
            if candidate not in taken:
                break
        taken.add(candidate)
        record = build_record(entry, candidate)
        record["_tradition"] = entry["tradition"]
        written.append(record)
        if not args.dry_run:
            path = ENTRIES / f"{candidate}.json"
            clean = {key: value for key, value in record.items() if not key.startswith("_")}
            path.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{'Would write' if args.dry_run else 'Wrote'} {len(written)} new records, "
          f"{len(wanted) - len(written) - len(skipped)} already had a record, skipped {len(skipped)}")
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
    print("By start century: " + ", ".join(f"{c} {n}" for c, n in centuries.items()))
    regions = Counter(region(r["location"]["lat"], r["location"]["lon"]) for r in written)
    print("By region: " + ", ".join(f"{name} {n}" for name, n in regions.most_common()))
    traditions = Counter(r["_tradition"] or "encyclopedia only" for r in written)
    print("By curated tradition: " + ", ".join(f"{name} {n}" for name, n in traditions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
