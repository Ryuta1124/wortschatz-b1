"""Build the single-file app by inserting word data into app/template.html.

Usage:
    python scripts/build.py                     # uses data/words.json, else the sample
    python scripts/build.py path/to/words.json

Writes dist/wortschatz.html, which opens directly in a browser (no server needed).

Each row of the data is:
    [German, English, Japanese, type, example (German), example (English), level, plural]
type is "n" (noun), "v" (verb) or "o" (other); level is "A1", "A2" or "B1";
plural is the plural noun without article ("Äpfel"), or "" when there is none.
Rows with only the first 7 fields are accepted (no plural questions for them).
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) > 1:
        source = pathlib.Path(sys.argv[1])
    elif (ROOT / "data" / "words.json").exists():
        source = ROOT / "data" / "words.json"
    else:
        source = ROOT / "data" / "sample-words.json"
    rows = json.loads(source.read_text(encoding="utf-8"))
    for i, row in enumerate(rows):
        if len(row) not in (7, 8):
            sys.exit(f"{source}: row {i} has {len(row)} fields, expected 7 or 8")
    template = (ROOT / "app" / "template.html").read_text(encoding="utf-8")
    marker = "/*DATA*/[]"
    if marker not in template:
        sys.exit("app/template.html: data marker not found")
    html = template.replace(marker, json.dumps(rows, ensure_ascii=False, separators=(",", ":")))
    out = ROOT / "dist" / "wortschatz.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"{len(rows)} words from {source.name} -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
