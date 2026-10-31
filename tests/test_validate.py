"""Record checks in pipeline/validate.py: the year rules (BCE, no year 0) and the disputed-claims rules."""

import datetime
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import validate

SCHEMA = json.loads(validate.SCHEMA.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)


def record(**changes):
    base = {
        "id": "socrates", "wikidata": "Q913", "name": "Socrates", "category": "philosopher",
        "start": -470, "end": -399, "date_precision": "year",
        "location": {"lat": 37.97, "lon": 23.72, "place": "Athens"},
        "summary": "Athenian philosopher.",
        "links": {"wikipedia": "https://en.wikipedia.org/wiki/Socrates"},
        "sources": ["https://www.wikidata.org/wiki/Q913"],
        "disputed": False,
    }
    base.update(changes)
    return base


def problems_for(rec, filename="socrates.json"):
    return validate.check_entry(Path(filename), rec, VALIDATOR)


def test_socrates_passes():
    assert problems_for(record()) == []


@pytest.mark.parametrize("start,end", [(-1, 1), (-1, -1), (1, 1), (-3000, -2000)])
def test_bce_and_ce_years_around_the_missing_year_zero(start, end):
    assert validate.check_years({"start": start, "end": end}) == []


def test_year_zero_rejected_in_start_end_and_claims():
    assert any("no year 0" in p for p in validate.check_years({"start": 0}))
    assert any("end" in p and "no year 0" in p for p in validate.check_years({"start": -5, "end": 0}))
    claim = {"start": -5, "claims": [{"value": 0}]}
    assert any("claims/0/value" in p for p in validate.check_years(claim))


def test_start_after_end_rejected():
    assert any("is after end" in p for p in validate.check_years({"start": -399, "end": -470}))


def test_future_year_rejected():
    future = datetime.date.today().year + 1
    assert any("in the future" in p for p in validate.check_years({"start": future}))


def test_id_must_equal_file_name():
    assert any("must equal the file name" in p for p in problems_for(record(), "plato.json"))


def test_schema_error_short_circuits_other_rules():
    broken = record(sources=[])
    problems = problems_for(broken, "wrong-name.json")
    assert problems and not any("file name" in p for p in problems)


def test_disputed_needs_claims_and_claims_need_disputed():
    assert any("needs at least two claims" in p for p in problems_for(record(disputed=True)))
    claims = [
        {"field": "start", "value": -1611, "sources": ["https://example.org/a"]},
        {"field": "start", "value": -1500, "sources": ["https://example.org/b"]},
    ]
    assert any("only for disputed" in p for p in problems_for(record(claims=claims)))
    assert problems_for(record(disputed=True, claims=claims)) == []


def test_unknown_category_rejected():
    assert problems_for(record(category="wizard"))


def test_every_category_in_schema_is_known_to_the_site():
    schema_categories = set(SCHEMA["properties"]["category"]["enum"])
    site = (Path(__file__).resolve().parent.parent / "site" / "js" / "categories.js").read_text(encoding="utf-8")
    for category in schema_categories:
        assert f'["{category}"' in site, f"site/js/categories.js is missing '{category}'"
