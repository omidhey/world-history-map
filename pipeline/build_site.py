"""Copy the data the web page needs into site/data/ (generated, git-ignored).

Run from the repository root:  python pipeline/build_site.py
The GitHub Pages workflow runs the same script before publishing site/.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BORDERS_IN = ROOT / "data" / "borders"
BORDERS_OUT = ROOT / "site" / "data" / "borders"


def main() -> None:
    if BORDERS_OUT.exists():
        shutil.rmtree(BORDERS_OUT)
    BORDERS_OUT.mkdir(parents=True)

    manifest = json.loads((BORDERS_IN / "manifest.json").read_text(encoding="utf-8"))
    for snapshot in manifest["snapshots"]:
        shutil.copy2(BORDERS_IN / snapshot["file"], BORDERS_OUT / snapshot["file"])
    shutil.copy2(BORDERS_IN / "manifest.json", BORDERS_OUT / "manifest.json")
    print(f"Copied {len(manifest['snapshots'])} snapshots to {BORDERS_OUT}")


if __name__ == "__main__":
    main()
