"""Check every record in data/entries/ before it can be merged.

Run from the repository root:  python pipeline/validate.py
The pull-request check (.github/workflows/validate.yml) runs the same script.
Prints one line per problem and exits with status 1 if there are any.

Checks: the JSON Schema in pipeline/entry.schema.json, plus rules a schema cannot express:
no year 0, start not after end, id equals the file name, no duplicate ids or Wikidata ids,
disputed records carry their claims, and every border override has a source.
Polities in data/polities/ follow pipeline/polity.schema.json with the same year rules, and every
border name they list must exist in the snapshots and be claimed by only one polity at a time.
Dynasties (data/dynasties/) and rulers (data/rulers/) name a polity that exists, a ruler's dynasty
belongs to the same polity, and reigns lie within the state's dates give or take REIGN_SLACK years.
"""

import datetime
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
OVERRIDES = ROOT / "data" / "borders" / "overrides.json"
POLITIES = ROOT / "data" / "polities"
BORDERS = ROOT / "data" / "borders"
SCHEMA = Path(__file__).resolve().parent / "entry.schema.json"
POLITY_SCHEMA = Path(__file__).resolve().parent / "polity.schema.json"
DYNASTIES = ROOT / "data" / "dynasties"
RULERS = ROOT / "data" / "rulers"
DYNASTY_SCHEMA = Path(__file__).resolve().parent / "dynasty.schema.json"
RULER_SCHEMA = Path(__file__).resolve().parent / "ruler.schema.json"
REIGN_SLACK = 30  # years a reign may fall outside its state's dates (states have fuzzy edges)


def check_years(record: dict) -> list[str]:
    problems = []
    years = {"start": record["start"]}
    if "end" in record:
        years["end"] = record["end"]
    for i, claim in enumerate(record.get("claims", [])):
        years[f"claims/{i}/value"] = claim["value"]
    this_year = datetime.date.today().year
    for field, year in years.items():
        if year == 0:
            problems.append(f"{field}: there is no year 0 (1 BCE is -1, 1 CE is 1)")
        if year > this_year:
            problems.append(f"{field}: {year} is in the future")
    if "end" in record and record["start"] > record["end"]:
        problems.append(f"start {record['start']} is after end {record['end']}")
    return problems


def check_entry(path: Path, record: dict, validator: Draft202012Validator) -> list[str]:
    problems = []
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in error.absolute_path) or "record"
        problems.append(f"{where}: {error.message}")
    if problems:
        return problems  # the rules below assume the basic shape is right

    if record["id"] != path.stem:
        problems.append(f"id '{record['id']}' must equal the file name '{path.stem}'")

    problems += check_years(record)

    if record.get("claims") and not record.get("disputed"):
        problems.append("claims are only for disputed records: set disputed: true")
    if record.get("disputed") and not record.get("claims"):
        problems.append("disputed: true needs at least two claims, each with its own source")
    return problems


def check_overrides() -> list[str]:
    problems = []
    for override in json.loads(OVERRIDES.read_text(encoding="utf-8")):
        if not override.get("sources"):
            problems.append(f"{OVERRIDES.relative_to(ROOT).as_posix()}: override '{override.get('id')}' has no sources")
    return problems


def border_name_years() -> dict[str, set[int]]:
    """Every NAME that appears in the border snapshots -> the snapshot years it appears in."""
    names: dict[str, set[int]] = {}
    for path in BORDERS.glob("world_*.geojson"):
        year = int(path.stem.split("_", 1)[1])
        for feature in json.loads(path.read_text(encoding="utf-8"))["features"]:
            name = feature["properties"].get("NAME")
            if name:
                names.setdefault(name, set()).add(year)
    return names


def check_polities() -> tuple[int, list[str]]:
    validator = Draft202012Validator(json.loads(POLITY_SCHEMA.read_text(encoding="utf-8")))
    known = border_name_years()
    problems = []
    seen_ids: dict[str, str] = {}
    seen_wikidata: dict[str, str] = {}
    claims: dict[str, list[tuple[int, int, str]]] = {}  # border name -> (start, end, polity id)
    files = sorted(POLITIES.glob("*.json"))
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            problems.append(f"{name}: not valid JSON ({error})")
            continue
        if not isinstance(record, dict):
            problems.append(f"{name}: must be one JSON object")
            continue
        found = check_entry(path, record, validator)
        problems += [f"{name}: {p}" for p in found]
        if found:
            continue
        for key, seen in (("id", seen_ids), ("wikidata", seen_wikidata)):
            value = record.get(key)
            if isinstance(value, str):
                if value in seen:
                    problems.append(f"{name}: duplicate {key} '{value}' (also in {seen[value]})")
                else:
                    seen[value] = name
        end = record.get("end", 9999)
        for border_name in record["border_names"]:
            if border_name not in known:
                problems.append(f"{name}: border name '{border_name}' does not appear in any snapshot in data/borders/")
            claims.setdefault(border_name, []).append((record["start"], end, record["id"]))

    for border_name, holders in sorted(claims.items()):
        holders.sort()
        for (s1, e1, id1), (s2, e2, id2) in zip(holders, holders[1:]):
            if s2 <= e1:
                problems.append(f"border name '{border_name}' is claimed by both '{id1}' and '{id2}' at overlapping dates")
    return len(files), problems


def check_rulers() -> tuple[int, list[str]]:
    """Dynasties and rulers: schema, then links to polities and dynasties and dates that fit the state."""
    polities = {}
    for path in POLITIES.glob("*.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        polities[record["id"]] = record
    problems, dynasties = [], {}
    count = 0
    for folder, schema_path in ((DYNASTIES, DYNASTY_SCHEMA), (RULERS, RULER_SCHEMA)):
        validator = Draft202012Validator(json.loads(schema_path.read_text(encoding="utf-8")))
        seen_wikidata: dict[str, str] = {}
        for path in sorted(folder.glob("*.json")):
            count += 1
            name = path.relative_to(ROOT).as_posix()
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                problems.append(f"{name}: not valid JSON ({error})")
                continue
            if not isinstance(record, dict):
                problems.append(f"{name}: must be one JSON object")
                continue
            found = check_entry(path, record, validator)
            problems += [f"{name}: {p}" for p in found]
            if found:
                continue
            if folder is DYNASTIES:
                dynasties[record["id"]] = record
            qid = record.get("wikidata")
            if qid:
                if qid in seen_wikidata:
                    problems.append(f"{name}: duplicate wikidata '{qid}' (also in {seen_wikidata[qid]})")
                seen_wikidata[qid] = name
    for folder in (DYNASTIES, RULERS):
        for path in sorted(folder.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict) or "polity" not in record or "id" not in record:
                continue
            name = path.relative_to(ROOT).as_posix()
            polity = polities.get(record["polity"])
            if not polity:
                problems.append(f"{name}: polity '{record['polity']}' has no record in data/polities/")
                continue
            low, high = polity["start"] - REIGN_SLACK, polity.get("end", 9999) + REIGN_SLACK
            end = record.get("end", record.get("start"))
            if isinstance(record.get("start"), int) and not (low <= record["start"] <= high and (not isinstance(end, int) or end <= high)):
                problems.append(f"{name}: dates {record['start']}..{record.get('end', '')} fall outside {polity['name']} ({polity['start']}..{polity.get('end', '')}) by more than {REIGN_SLACK} years")
            if folder is RULERS and "dynasty" in record:
                dynasty = dynasties.get(record["dynasty"])
                if not dynasty:
                    problems.append(f"{name}: dynasty '{record['dynasty']}' has no record in data/dynasties/")
                elif dynasty["polity"] != record["polity"]:
                    problems.append(f"{name}: dynasty '{record['dynasty']}' belongs to '{dynasty['polity']}', not '{record['polity']}'")
    return count, problems


def check_lineage() -> tuple[int, list[str]]:
    """Each data/lineage/<ISO>.json and data/lineage_curated/<ISO>.json: snapshot years exist in the manifest,
    every share is in (0, 1]. Curated files also need source URLs and state names that exist in that snapshot."""
    manifest = json.loads((ROOT / "data" / "borders" / "manifest.json").read_text(encoding="utf-8"))
    years = {str(s["year"]) for s in manifest["snapshots"]}
    files = {str(s["year"]): s["file"] for s in manifest["snapshots"]}
    names_cache: dict[str, set] = {}
    problems, count = [], 0
    for folder_name in ("lineage", "lineage_curated"):
        folder = ROOT / "data" / folder_name
        curated = folder_name == "lineage_curated"
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name == "index.json":
                continue
            count += 1
            name = f"data/{folder_name}/{path.name}"
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                problems.append(f"{name}: not valid JSON ({error})")
                continue
            if record.get("country") != path.stem:
                problems.append(f"{name}: country '{record.get('country')}' must equal the file name")
            if curated:
                if record.get("source") != "curated":
                    problems.append(f"{name}: source must be 'curated'")
                if not any(str(u).startswith("http") for u in record.get("sources", [])):
                    problems.append(f"{name}: needs at least one source URL")
                for year in record.get("notes", {}):
                    if year not in record.get("snapshots", {}):
                        problems.append(f"{name}: note for {year}, which has no snapshot")
            for year, entries in record.get("snapshots", {}).items():
                if year not in years:
                    problems.append(f"{name}: snapshot {year} is not in data/borders/manifest.json")
                    continue
                if curated and year not in names_cache:
                    geo = json.loads((ROOT / "data" / "borders" / files[year]).read_text(encoding="utf-8"))
                    names_cache[year] = {f["properties"].get("NAME") for f in geo["features"]}
                for entry in entries:
                    if not 0 < entry.get("share", 0) <= 1.0001:
                        problems.append(f"{name}: {year}: share {entry.get('share')} for '{entry.get('name')}' is not in (0, 1]")
                    if curated and entry.get("name") not in names_cache[year]:
                        problems.append(f"{name}: {year}: '{entry.get('name')}' is not a state name in that snapshot")
    return count, problems


def check_areas() -> tuple[int, list[str]]:
    """data/areas/areas.json: polity ids exist, years are snapshot years, numbers are whole and not negative."""
    path = ROOT / "data" / "areas" / "areas.json"
    if not path.exists():
        return 0, []
    manifest = json.loads((ROOT / "data" / "borders" / "manifest.json").read_text(encoding="utf-8"))
    years = {str(s["year"]) for s in manifest["snapshots"]}
    polities = {p.stem for p in (ROOT / "data" / "polities").glob("*.json")}
    problems = []
    areas = json.loads(path.read_text(encoding="utf-8"))
    for polity, by_year in areas.items():
        if polity not in polities:
            problems.append(f"data/areas/areas.json: '{polity}' is not a polity")
        for year, entry in by_year.items():
            if year not in years:
                problems.append(f"data/areas/areas.json: {polity}: {year} is not a snapshot year")
            for key in ("area_km2", "carried_km2", "gained_km2", "lost_km2"):
                if key in entry and (not isinstance(entry[key], int) or entry[key] < 0):
                    problems.append(f"data/areas/areas.json: {polity}: {year}: {key} must be a whole number >= 0")
            if "area_km2" not in entry:
                problems.append(f"data/areas/areas.json: {polity}: {year}: area_km2 is missing")
    return len(areas), problems


def main() -> int:
    validator = Draft202012Validator(json.loads(SCHEMA.read_text(encoding="utf-8")))
    problems = []
    seen_ids: dict[str, str] = {}
    seen_wikidata: dict[str, str] = {}
    files = sorted(ENTRIES.glob("*.json"))

    for path in files:
        name = path.relative_to(ROOT).as_posix()
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            problems.append(f"{name}: not valid JSON ({error})")
            continue
        if not isinstance(record, dict):
            problems.append(f"{name}: must be one JSON object")
            continue
        problems += [f"{name}: {p}" for p in check_entry(path, record, validator)]

        for key, seen in (("id", seen_ids), ("wikidata", seen_wikidata)):
            value = record.get(key)
            if isinstance(value, str):
                if value in seen:
                    problems.append(f"{name}: duplicate {key} '{value}' (also in {seen[value]})")
                else:
                    seen[value] = name

    problems += check_overrides()
    polity_count, polity_problems = check_polities()
    problems += polity_problems
    ruler_count, ruler_problems = check_rulers()
    problems += ruler_problems
    lineage_count, lineage_problems = check_lineage()
    problems += lineage_problems
    area_count, area_problems = check_areas()
    problems += area_problems

    for problem in problems:
        print(problem)
    print(f"Checked {len(files)} entries and {polity_count} polities and {ruler_count} dynasties and rulers and {lineage_count} lineages and {area_count} area series:{len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
