"""Smoke tests on the real data/ directory."""

import validate


def test_real_data_validates(capsys):
    assert validate.main() == 0, capsys.readouterr().out


def test_every_entry_file_name_is_its_id():
    import json
    for path in validate.ENTRIES.glob("*.json"):
        assert json.loads(path.read_text(encoding="utf-8"))["id"] == path.stem
