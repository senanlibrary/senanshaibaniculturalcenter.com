# Subject vocabulary: observations and recommendations

**Scope of this memo.** These are recommendations only. No vocabulary change
has been made to the catalog, and none will be made without the cataloging
team's agreement. The migration applied whitespace, casing, and duplicate
fixes only; every subject term entered by the catalogers survives intact.

Prepared during the migration of the catalog off WordPress, against the
890-record Rifʿat al-Saʿīd Library export.

---

## What the data shows

| Measure | Value |
|---|---|
| Records | 890 |
| Records with at least one subject term | 451 (51%) |
| Distinct subject terms | 756 |
| Terms used exactly once | 554 (73%) |

A vocabulary where roughly three out of four terms appear on a single record
is doing the work of a note field rather than an index. This is an expected
and normal result of MPLP-style cataloging at speed, and it is easily
addressed — but it does mean subject terms cannot yet drive browsing.

## Specific issues

**1. Case and punctuation variants split identical concepts.**
`History` (65 records) and `HISTORY` (1) are separate terms, as are
`Periodicals` (19) and `periodicals` (4). Seventeen such clusters exist. These
are safe to merge mechanically and the migration already does so at search
time; merging them at source would make the facet counts correct too.

**2. A small number of terms are malformed.**
Values including `(Iraq :`, `1958)`, `1920)`, `5.200`, and `6` appear to be
fragments captured during import rather than intended headings.

**3. Four different kinds of term share one field.**
The `Subject Tags` field currently mixes:

- *Places* — Iraq (44), Egypt (39), Lebanon (10), Arab countries (51)
- *Topics* — Politics and government (77), Islam (25), Communism (10)
- *Periods* — `20th century` (13), `1945-` (11), `1979-` (10)
- *Forms* — Periodicals (19)

Because they are undifferentiated, a reader cannot ask for "Egyptian material
about journalism from the 1960s" — the three concepts are not separable.

**4. Arabic and English terms for the same concept do not co-retrieve.**
`History` and `تاريخ`, `Iraq` and `العراق`, `Islam` and `الاسلام` are
independent terms. There are also Arabic-internal variants — `الاسلام` and
`الإسلام` differ only in hamza, `تاريخ` and `التاريخ` only in the definite
article. Roughly 60% of this collection is Arabic-language, so this split
affects the majority of the holdings.

The new site mitigates this in *search* by folding hamza, alef forms, ta
marbuta, and diacritics, and by bridging scripts with a consonant skeleton, so
`sahafah` and `صحافة` return the same 38 records. That is a retrieval
workaround, not a cataloging fix — the underlying terms remain distinct.

## Recommendations, in priority order

**A. Merge case and punctuation variants, and repair the malformed values.**
Roughly 20 records affected. Purely mechanical, no judgment required, no risk
to intellectual content. This alone makes the facet counts trustworthy.

**B. Split the single subject field into four: Place, Topic, Period, Form.**
Zotero can carry these as prefixed tags (`place:Iraq`, `topic:Journalism`)
without any change of platform or workflow. This is the single highest-value
change: it turns 756 flat strings into browsable, combinable facets, and it is
what would let a researcher narrow by region and era at once.

**C. Adopt Library of Congress wording where an obvious equivalent exists.**
Not a full authority-controlled migration — that is disproportionate here —
but preferring LCSH phrasing for common headings (`Politics and government`,
`Foreign relations`, and `Intellectual life` already match) means the
collection's terms will align with what researchers meet in other catalogs,
and leaves the door open to formal authority control later.

**D. Pair Arabic and English terms.**
Where a concept is tagged in both scripts, record them as a pair so the two
retrieve together. Best done during cataloging rather than retroactively.

**E. Raise subject coverage before expanding it.**
With 49% of records carrying no subject term at all, adding terms to untagged
records will improve discovery more than refining terms on tagged ones.

## A note on sequencing

Recommendation A is safe to apply at any time. B is best decided before the
remaining collections are cataloged, since retrofitting facets across 10,000+
records costs far more than establishing the convention now, while the
catalog is at roughly 890.

Nothing here criticises the work done to date. Cataloging 890 items to this
level of descriptive detail — with shelf-level location, OCLC numbers, and
parallel Arabic and romanized titles — is a substantial achievement, and the
issues above are the ordinary consequence of building a vocabulary while
also building the collection.
