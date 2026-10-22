"""Check every record in data/entries/ before it can be merged.

Run from the repository root:  python pipeline/validate.py
The pull-request check (.github/workflows/validate.yml) runs the same script.
Prints one line per problem and exits with status 1 if there are any.

Checks: the JSON Schema in pipeline/entry.schema.json, plus rules a schema cannot express:
no year 0, start not after end, id equals the file name, no duplicate ids or Wikidata ids,
disputed records carry their claims, and every border override has a source.
"""

import datetime
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "data" / "entries"
OVERRIDES = ROOT / "data" / "borders" / "overrides.json"
SCHEMA = Path(__file__).resolve().parent / "entry.schema.json"


def check_entry(path: Path, record: dict, validator: Draft202012Validator) -> list[str]:
    problems = []
    for error in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in error.absolute_path) or "record"
        problems.append(f"{where}: {error.message}")
    if problems:
        return problems  # the rules below assume the basic shape is right

    if record["id"] != path.stem:
        problems.append(f"id '{record['id']}' must equal the file name '{path.stem}'")

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

    for problem in problems:
        print(problem)
    print(f"Checked {len(files)} entries: {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
