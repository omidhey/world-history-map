"""Contributor list from git history.

Writes data/contributors.json (copied to the site by build_site.py) and CONTRIBUTORS.md.
Identities are merged through .mailmap; e-mail addresses are never written out.
Run it before a release: python pipeline/make_contributors.py
"""

import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOT_MARKERS = ("[bot]", "github-actions")


def parse_names(log_output: str) -> list[dict]:
    """Turn `git log --format=%aN` output (one author name per commit) into ranked contributors."""
    counts = Counter(line.strip() for line in log_output.splitlines() if line.strip())
    for name in [n for n in counts if any(m in n.lower() for m in BOT_MARKERS)]:
        del counts[name]
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))
    return [{"name": name, "commits": commits} for name, commits in ranked]


def git_authors() -> str:
    return subprocess.run(
        ["git", "log", "--format=%aN"], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def markdown(people: list[dict]) -> str:
    lines = [
        "# Contributors",
        "",
        "Generated from git history by `pipeline/make_contributors.py`; do not edit by hand.",
        "People who suggested changes through issues are credited in the issue and pull request history.",
        "",
    ]
    lines += [f"- {p['name']} ({p['commits']} commits)" for p in people]
    return "\n".join(lines) + "\n"


def main() -> None:
    people = parse_names(git_authors())
    (ROOT / "data" / "contributors.json").write_text(
        json.dumps(people, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (ROOT / "CONTRIBUTORS.md").write_text(markdown(people), encoding="utf-8")
    print(f"Wrote {len(people)} contributors")


if __name__ == "__main__":
    main()
