"""Extract headwords and their first example sentence from a Goethe-style word list PDF.

The official word lists (Goethe-Zertifikat B1, DTZ, ...) are printed in two columns, and
each column has a headword column on the left and example sentences on the right.
This script:

  1. renders every page twice with `pdftotext -layout`, once cropped to the left half
     and once to the right half, so each text block is a single column;
  2. finds the x position where example sentences start in each column;
  3. joins wrapped headword lines (verb forms, hyphenation) into one entry;
  4. reduces each entry to a lemma ("der Apfel", "abholen", "sich freuen")
     and keeps its first example sentence.

Usage:
    python extract_wordlist.py LIST.pdf FIRST_PAGE LAST_PAGE out.json

Output: a JSON list of {"lemma": ..., "headword": ..., "example": ...}.
Requires `pdftotext` (poppler or xpdf) on PATH. The PDF itself is not part of this repo.
"""
import collections
import json
import re
import subprocess
import sys

HALF_PAGE = "297"  # half of an A4 page width in points


def page_columns(pdf, page):
    """Yield the text of the left and right column of one page."""
    for side in (["-marginr", HALF_PAGE], ["-marginl", HALF_PAGE]):
        cmd = ["pdftotext", "-enc", "UTF-8", "-layout", "-f", str(page), "-l", str(page), *side, pdf, "-"]
        yield subprocess.run(cmd, capture_output=True, check=True).stdout.decode("utf-8")


SKIP_LINE = re.compile(r"WORTLISTE|ZERTIFIKAT|VS_0|Alphabetisch|ALPHABETISCH|Ihre Notizen|9 WORTLISTEN")


def is_continuation(prev, line):
    """True when a headword line continues the previous entry (verb forms, wraps)."""
    return (
        prev.endswith((",", "→", ":"))
        or re.search(r"[a-zäöüß]-$", prev)
        or re.match(r"^(hat|ist|sind|haben|\(|→)", line)
        or re.match(r"^\S+, (hat|ist) ", line)
        or re.fullmatch(r"ge\w+", line)
    )


def parse_column(text, entries):
    lines = [l.rstrip().replace("\f", "") for l in text.split("\n")]
    starts = collections.Counter(m.start() for l in lines for m in re.finditer(r"\S+(?: \S+)*", l))
    frequent = [s for s, c in starts.items() if c >= 3]
    if not frequent:
        return
    head_x = min(frequent)
    later = [s for s, c in starts.most_common() if s > head_x + 12 and c >= 3]
    example_x = later[0] if later else 999

    current = None
    for line in lines:
        if not line.strip() or SKIP_LINE.search(line):
            continue
        segs = [(m.start(), m.group()) for m in re.finditer(r"\S+(?: \S+)*", line)]
        head = " ".join(t for x, t in segs if x < example_x - 2).strip()
        example = " ".join(t for x, t in segs if x >= example_x - 2)
        if not head:
            if example and entries:
                entries[-1]["parts"].append(example)
            continue
        if re.fullmatch(r"[A-ZÄÖÜ]", head) or re.match(r"^\d+\.", head):
            continue  # section letter or numbered example line
        if current is not None and is_continuation(current["headword"], head):
            current["headword"] += " " + head
            if example:
                current["parts"].append(example)
        else:
            current = {"headword": head, "parts": [example] if example else []}
            entries.append(current)


def lemma(headword):
    h = re.sub(r"→.*", "", headword)
    h = re.sub(r"\((D|A|CH|Pl\.|nur Pl\.|Sg\.)[^)]*\)", "", h)
    lem = re.split(r"\s\d\.\s", h.split(",")[0].strip())[0]
    tokens = lem.split()
    if not tokens:
        return ""
    if tokens[0].strip("()") in ("der", "die", "das", "sich") and len(tokens) >= 2:
        return " ".join(tokens[:2]).replace("(", "").replace(")", "")
    return tokens[0] if len(tokens) > 3 else lem


def first_example(entry):
    h = entry["headword"]
    glued = re.search(r"\s(\d\.\s.*)$", h) or re.search(r"^(?:der|die|das)\s+\S+,\s*\S+\s+([A-ZÄÖÜ„].*)$", h)
    text = " ".join(([glued.group(1)] if glued else []) + entry["parts"])
    text = re.sub(r"([a-zäöüß])- ([a-zäöüß])", r"\1\2", text)  # undo hyphenation
    text = re.sub(r"\s+", " ", text).strip()
    for piece in (p.strip() for p in re.split(r"(?:^|\s)\d\.\s", text)):
        if re.match(r'^[A-ZÄÖÜ„–"0-9]', piece) and len(piece) <= 170 and re.search(r"[.!?…]$", piece):
            return piece
    return None


def main(pdf, first, last, out):
    entries = []
    for page in range(int(first), int(last) + 1):
        for column in page_columns(pdf, page):
            parse_column(column, entries)
    result, seen = [], set()
    for e in entries:
        lem = lemma(e["headword"])
        if len(lem) < 2 or lem.lower() in seen:
            continue
        seen.add(lem.lower())
        result.append({"lemma": lem, "headword": e["headword"], "example": first_example(e)})
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print(f"{len(result)} entries, {sum(1 for r in result if r['example'])} with an example")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
