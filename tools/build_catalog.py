#!/usr/bin/env python3
"""Turn a Zotero CSV export into the catalog JSON the site consumes.

Zotero is the system of record. This script is deterministic and re-runnable:
drop in a fresh export, run it, and every normalization below is re-applied.
Nothing here edits the export in place, so catalogers' work is never
overwritten and this script's work is never lost.

Scope is deliberately minimal. Per the center's decision, the subject
vocabulary developed by the cataloging team is left intact -- only whitespace,
duplicate, and encoding issues are corrected. Vocabulary changes require the
cataloging team's agreement before they are added here.
"""
import csv
import json
import re
import sys
import unicodedata
from collections import Counter

# --- Arabic script handling -------------------------------------------------

ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")
TASHKEEL_RE = re.compile(r"[ً-ْٰـ]")
ALEF_RE = re.compile(r"[آأإٱ]")

# Latin letters that carry scholarly transliteration marks but are not
# combining characters, so NFD alone will not remove them.
TRANSLIT_MARKS = str.maketrans(
    {c: None for c in "ʿʾʻʼ‘’'``"}
)


def has_arabic(s):
    return bool(ARABIC_RE.search(s or ""))


def fold_arabic(s):
    """Collapse orthographic variants so search matches how people type.

    Readers rarely type hamza seats or diacritics, and catalogers are not
    consistent about them either, so both sides are folded to a common form.
    """
    s = TASHKEEL_RE.sub("", s)
    s = ALEF_RE.sub("ا", s)
    s = s.replace("ى", "ي")  # alef maqsura -> ya
    s = s.replace("ة", "ه")  # ta marbuta   -> ha
    s = s.replace("ؤ", "و").replace("ئ", "ي")
    return s


def fold_latin(s):
    """Strip diacritics and transliteration marks: 'Ṣaḥāfah' -> 'sahafah'."""
    s = s.translate(TRANSLIT_MARKS)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", s).lower()


# A coarse consonantal romanization, used ONLY to widen the search index.
# It is never displayed and never written back to Zotero: an approximate
# romanization is a fine search bridge but would be false cataloging data.
# Without it, a researcher typing "sahafah" cannot reach a record whose title
# exists only as صحافة.
ROMAN_MAP = {
    "ا": "a", "ب": "b", "ت": "t", "ث": "th", "ج": "j", "ح": "h", "خ": "kh",
    "د": "d", "ذ": "dh", "ر": "r", "ز": "z", "س": "s", "ش": "sh", "ص": "s",
    "ض": "d", "ط": "t", "ظ": "z", "ع": "", "غ": "gh", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "y",
    "ء": "", "ﻻ": "la", "پ": "p", "چ": "ch", "ژ": "zh", "گ": "g",
}


def romanize(s):
    """Approximate Arabic script as Latin consonants for search only."""
    s = fold_arabic(s)
    out = [ROMAN_MAP.get(c, c if c.isspace() else "") for c in s]
    return re.sub(r"\s+", " ", "".join(out)).strip()


def skeleton(s):
    """Reduce Latin text to consonants.

    Unvocalized Arabic romanizes without short vowels, so 'صحافة' yields
    roughly 'shafh' while a reader types 'sahafah'. Comparing both sides as
    consonant skeletons ('shfh') is what makes the two meet.
    """
    return re.sub(r"[aeiou]", "", s)


def search_key(*parts):
    """Folded haystack: exact-ish matching, both scripts."""
    out = []
    for p in parts:
        if not p:
            continue
        p = str(p)
        out.append(fold_arabic(p) if has_arabic(p) else fold_latin(p))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


def skeleton_key(*parts):
    """Consonant-skeleton haystack: bridges script boundaries."""
    out = []
    for p in parts:
        if not p:
            continue
        p = str(p)
        out.append(skeleton(romanize(p) if has_arabic(p) else fold_latin(p)))
    return re.sub(r"\s+", " ", " ".join(out)).strip()


# --- Field normalization ----------------------------------------------------

# The export contains six spellings of two languages.
LANGUAGE_MAP = {
    "ara": "Arabic",
    "arabic": "Arabic",
    "ar": "Arabic",
    "eng": "English",
    "english": "English",
    "en": "English",
    "fre": "French",
    "fra": "French",
    "fr": "French",
    "french": "French",
    "ger": "German",
    "deu": "German",
    "de": "German",
    "german": "German",
    "tur": "Turkish",
    "turkish": "Turkish",
    "jpn": "Japanese",
    "japanese": "Japanese",
    "dan": "Danish",
    "da": "Danish",
    "rus": "Russian",
    "ita": "Italian",
    "spa": "Spanish",
    "heb": "Hebrew",
    "per": "Persian",
    "fas": "Persian",
    "kur": "Kurdish",
}


def normalize_languages(raw):
    """'en/ara' and 'ara;eng' both mean the same pair of languages."""
    if not raw or not raw.strip():
        return []
    parts = re.split(r"[;,/]| and ", raw.lower())
    seen = []
    for p in parts:
        p = p.strip(" .;,")
        # Stray punctuation and single characters are data entry noise, not
        # languages; dropping them keeps the facet list usable.
        if len(p) < 2:
            continue
        name = LANGUAGE_MAP.get(p, p.title())
        if name not in seen:
            seen.append(name)
    return seen


def normalize_tags(raw):
    """Split, trim, drop empties, dedupe case-insensitively, keep order.

    Vocabulary itself is left untouched by design.
    """
    if not raw:
        return []
    out, seen = [], set()
    for t in raw.split(";"):
        t = re.sub(r"\s+", " ", t).strip().strip(".,")
        if not t:
            continue
        k = t.casefold()
        if k not in seen:
            seen.add(k)
            out.append(t)
    return out


def normalize_oclc(raw):
    """'OCLC: 51818732' -> '51818732'."""
    if not raw:
        return ""
    m = re.search(r"(\d{4,})", raw)
    return m.group(1) if m else ""


LATIN_RE = re.compile(r"[A-Za-zÀ-ɏḀ-ỿ]")


def split_parallel_title(title):
    """Separate 'Transliteration/العنوان' into its two scripts.

    Catalogd titles routinely carry romanized and Arabic forms joined by a
    slash. Keeping them apart lets each be typeset in its own script and
    direction instead of forcing a mixed-direction line.

    The source is not always well formed: some titles begin with a stray
    slash, and some run the two scripts together with no separator at all
    ("al-Khalījلعنة وطن"). Both are handled here rather than left to the
    browser, which would otherwise reorder the whole line.
    """
    title = title.strip().strip("/").strip()
    if not title:
        return ("", "")

    if "/" in title:
        left, _, right = title.partition("/")
        left, right = left.strip(), right.strip()
        if left and right and has_arabic(right) and not has_arabic(left):
            return (left, right)
        if left and right and has_arabic(left) and not has_arabic(right):
            return (right, left)

    # No usable separator: if the string runs Latin straight into Arabic,
    # split at that boundary.
    m = ARABIC_RE.search(title)
    if m and m.start() > 0:
        head, tail = title[: m.start()], title[m.start() :]
        if len(LATIN_RE.findall(head)) >= 6 and not LATIN_RE.search(tail):
            return (head.strip().strip("/:;,").strip(), tail.strip())

    if has_arabic(title) and not LATIN_RE.search(title):
        return ("", title)
    return (title, "")


def normalize_location(raw):
    """'Range 2, Shelf B' -> sortable components plus the display string."""
    m = re.search(r"Range\s*(\d+)[,\s]*Shelf\s*([A-Za-z]+)", raw or "", re.I)
    if not m:
        return {"display": (raw or "").strip(), "range": None, "shelf": None}
    return {
        "display": f"Range {m.group(1)}, Shelf {m.group(2).upper()}",
        "range": int(m.group(1)),
        "shelf": m.group(2).upper(),
    }


# Invisible bidirectional controls appear in a handful of records. They are
# unprintable but change how a whole line is laid out, so they are removed
# rather than passed through to the page.
BIDI_CONTROLS = re.compile(r"[‎‏‪-‮⁦-⁩]")


def clean(s):
    s = BIDI_CONTROLS.sub("", s or "")
    return re.sub(r"\s+", " ", s.strip())


def parse_year(raw):
    m = re.search(r"(1[0-9]{3}|20[0-9]{2})", raw or "")
    return int(m.group(1)) if m else None


def split_people(raw):
    if not raw:
        return []
    return [clean(p) for p in raw.split(";") if clean(p)]


# --- Build ------------------------------------------------------------------


def build(rows):
    items, report = [], Counter()
    for r in rows:
        title_latin, title_arabic = split_parallel_title(clean(r.get("Title")))
        authors = split_people(r.get("Author"))
        langs = normalize_languages(r.get("Language"))
        tags = normalize_tags(r.get("Subject Tags"))
        loc = normalize_location(r.get("Archive Location"))

        if r.get("Language", "").strip() and r["Language"].strip() not in (
            "ara",
            "eng",
        ):
            report["language_normalized"] += 1
        if title_arabic:
            report["parallel_titles_split"] += 1
        raw_tags = [t for t in (r.get("Subject Tags") or "").split(";")]
        if len([t for t in raw_tags if t.strip()]) != len(tags):
            report["tag_lists_deduped"] += 1

        searchable = (
            title_latin,
            title_arabic,
            " ".join(authors),
            clean(r.get("Publisher")),
            " ".join(tags),
            clean(r.get("Series")),
            normalize_oclc(r.get("OCLC")),
            clean(r.get("ISBN")),
        )

        items.append(
            {
                "id": clean(r.get("Key")),
                "title": title_latin,
                "titleArabic": title_arabic,
                "authors": authors,
                "editors": split_people(r.get("Editor")),
                "contributors": split_people(r.get("Contributor")),
                "year": parse_year(r.get("Date")),
                "date": clean(r.get("Date")),
                "publisher": clean(r.get("Publisher")),
                "place": clean(r.get("Place")),
                "series": clean(r.get("Series")),
                "pages": clean(r.get("Num Pages")),
                "isbn": clean(r.get("ISBN")),
                "issn": clean(r.get("ISSN")),
                "oclc": normalize_oclc(r.get("OCLC")),
                "languages": langs,
                "library": clean(r.get("Archive")),
                "location": loc,
                "subjects": tags,
                "itemType": clean(r.get("Item Type")) or "book",
                "search": search_key(*searchable),
                "skeleton": skeleton_key(*searchable),
            }
        )

    items.sort(key=lambda i: (i["title"] or i["titleArabic"] or "").casefold())
    return items, report


def facets(items):
    def tally(key):
        c = Counter()
        for i in items:
            v = key(i)
            for x in v if isinstance(v, list) else [v]:
                if x:
                    c[x] += 1
        return [{"value": k, "count": n} for k, n in c.most_common()]

    return {
        "libraries": tally(lambda i: i["library"]),
        "languages": tally(lambda i: i["languages"]),
        "subjects": tally(lambda i: i["subjects"]),
        "ranges": tally(
            lambda i: f"Range {i['location']['range']}" if i["location"]["range"] else ""
        ),
        "decades": tally(lambda i: f"{i['year'] // 10 * 10}s" if i["year"] else ""),
    }


def main(src, out):
    with open(src, encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    items, report = build(rows)
    f = facets(items)

    with open(out, "w", encoding="utf-8") as fh:
        json.dump(
            {"items": items, "facets": f, "count": len(items)},
            fh,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    print(f"{len(items)} records -> {out}")
    for k, v in sorted(report.items()):
        print(f"  {k.replace('_', ' '):24} {v}")
    print(f"  {'distinct subjects':24} {len(f['subjects'])}")
    print(f"  {'languages':24} {[x['value'] for x in f['languages']]}")
    arabic = sum(1 for i in items if i["titleArabic"] or has_arabic(i["title"]))
    print(f"  {'records w/ Arabic script':24} {arabic}")


if __name__ == "__main__":
    main(
        sys.argv[1] if len(sys.argv) > 1 else "data/zotero-export-rifat-al-said.csv",
        sys.argv[2] if len(sys.argv) > 2 else "data/catalog.json",
    )
