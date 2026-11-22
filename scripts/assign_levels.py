"""Assign a CEFR level (A1 / A2 / B1) to every word in the app data.

A word is A1 if it is a headword in the A1 list (Start Deutsch 1), otherwise A2 if it is
a headword in the A2 list, otherwise B1.

Usage:
    pdftotext -enc UTF-8 -layout A1_Wortliste.pdf a1.txt
    pdftotext -enc UTF-8 -layout A2_Wortliste.pdf a2.txt
    python assign_levels.py words.json a1.txt a2.txt

`words.json` is the app data (a list of rows whose first field is the German word);
the level is written into field 7 of each row. Front-matter pages are skipped by
looking only at lines from the word list sections.
"""
import collections
import json
import re
import sys


def norm(word):
    word = word.lower().replace("(", "").replace(")", "")
    word = re.sub(r"^(der|die|das|sich)\s+", "", word)
    word = re.sub(r"^(der|die|das)\s+", "", word)
    return word.strip(" .!-,")


def headwords(text_file):
    """Collect everything that looks like a headword (not an example sentence)."""
    found = set()
    for line in open(text_file, encoding="utf-8"):
        for seg in re.split(r"\s{2,}", line.strip()):
            seg = seg.strip()
            if not seg:
                continue
            # "die Apotheke, -n Das Medikament ..." -> headword glued to its example
            m = re.match(r"^(der|die|das)\s+([A-ZÄÖÜ][\w\-]*)\s*,", seg) or re.match(r"^([a-zäöüß][\w\-]*),\s", seg)
            if m:
                found.add(norm(m.group(0).rstrip(",").strip()))
            if (re.search(r"[.?!:]$", seg) and len(seg.split()) > 1) or len(seg.split()) > 5:
                continue  # an example sentence
            seg = re.sub(r"\((D|A|CH|Sg\.|Pl\.)[^)]*\)", "", seg)
            for part in seg.split("/"):
                lem = re.sub(r"\s+[-–¨\"].*$", "", part.split(",")[0].strip())
                if lem:
                    found.add(norm(lem))
    return found


def main(words_file, a1_txt, a2_txt):
    a1, a2 = headwords(a1_txt), headwords(a2_txt)
    rows = json.load(open(words_file, encoding="utf-8"))
    for row in rows:
        key = norm(row[0])
        level = "A1" if key in a1 else "A2" if key in a2 else "B1"
        row[6:] = [level]
    json.dump(rows, open(words_file, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(collections.Counter(r[6] for r in rows))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
