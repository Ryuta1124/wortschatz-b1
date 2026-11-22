"""Add plural forms to the app data from the plural markers in the word lists.

The lists mark plurals after the headword: B1 writes `der Apfel, ¨-` and `die Wohnung, -en`,
DTZ writes `der Ball, -"e`. `¨` or `"` means umlaut on the last a/o/u (au -> äu),
the rest is the ending. Full forms (`Museen`, `Bauten`) are used as they are;
entries with two possible plurals (`-s/-e`) are skipped.

Usage:
    python extract_wordlist.py B1_Wortliste.pdf 16 102 b1_entries.json
    python extract_wordlist.py DTZ_Wortliste.pdf 1 82 dtz_entries.json
    python add_plurals.py data/words.json b1_entries.json dtz_entries.json

Writes the plural (without article) into field 8 of each row, "" when unknown.
"""
import json
import re
import sys


def umlaut(word):
    low = word.lower()
    for i in range(len(low) - 1, -1, -1):
        if low[i] not in "aou":
            continue
        if low[i] == "u" and i > 0 and low[i - 1] == "a":  # au -> äu
            return word[:i - 1] + ("Ä" if word[i - 1] == "A" else "ä") + word[i:]
        rep = {"a": "ä", "o": "ö", "u": "ü"}[low[i]]
        return word[:i] + (rep.upper() if word[i].isupper() else rep) + word[i + 1:]
    return None


def plural(noun, marker):
    if "/" in marker:
        return None                      # two possible plurals
    if re.match(r"^[A-ZÄÖÜ]", marker):
        return marker                    # full form, e.g. Museen
    has_umlaut = "¨" in marker or '"' in marker
    suffix = marker.replace("¨", "").replace('"', "").lstrip("-").strip()
    if suffix == "nen":
        return None                      # feminine -in forms are not in the app
    base = umlaut(noun) if has_umlaut else noun
    if base is None:
        return None
    if suffix == "sse" and base.endswith("ss"):
        return base[:-2] + "sse"         # der Abschluss, -"sse -> Abschlüsse
    return base + suffix


def markers(entries_file):
    found = {}
    for entry in json.load(open(entries_file, encoding="utf-8")):
        m = re.match(r"^(der|die|das) ([A-ZÄÖÜ][^\s,]*)\s*,\s*([^\s(→]+)", entry["headword"])
        if m:
            found.setdefault(f"{m.group(1)} {m.group(2)}", m.group(3).rstrip(","))
    return found


def main(words_file, *entry_files):
    sources = [markers(f) for f in entry_files]
    rows = json.load(open(words_file, encoding="utf-8"))
    done = 0
    for row in rows:
        pl = ""
        if re.match(r"^(der|die|das) ", row[0]):
            marker = next((s[row[0]] for s in sources if row[0] in s), None)
            if marker:
                pl = plural(row[0].split()[1], marker) or ""
        row[7:] = [pl]
        done += bool(pl)
    json.dump(rows, open(words_file, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{done} nouns with a plural. Check unusual ones by hand (the extraction is not perfect).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
