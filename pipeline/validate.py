"""Check every record in data/entries/ before it can be merged.

Run from the repository root:  python pipeline/validate.py
The pull-request check (.github/workflows/validate.yml) runs the same script.
Prints one line per problem and exits with status 1 if there are any.

Checks: the JSON Schema in pipeline/entry.schema.json, plus rules a schema cannot express:
no year 0, start not after end, id equals the file name, no duplicate ids or Wikidata ids,
disputed records carry their claims, and every border override has a source.
Polities in data/polities/ follow pipeline/polity.schema.json with the same year rules, and every
border name they list must exist in the snapshots and be claimed by only one polity at a time.
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

    for problem in problems:
        print(problem)
    print(f"Checked {len(files)} entries and {polity_count} polities: {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
