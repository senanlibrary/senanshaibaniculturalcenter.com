#!/usr/bin/env python3
"""Post-build checks on the generated site.

These catch the mistakes that have actually happened here, rather than
anything theoretical. Run automatically after `npm run build`.
"""
import glob
import os
import re
import sys

# Resolved from this file, so the checks run the same whether invoked from
# the repository root or from site/ as an npm script.
DIST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site", "dist")


def read(path):
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return fh.read()


def strip_scripts(html):
    return re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.S)


def check_glued_links(pages):
    """Astro drops the whitespace before an inline <a> that starts a new
    source line, producing 'under aCC BY 4.0'. Easy to write, hard to see."""
    bad = []
    for path, html in pages:
        for m in re.finditer(r"[A-Za-z,;:]<a [^>]*>", strip_scripts(html)):
            start = max(0, m.start() - 28)
            bad.append((path, html[start : m.end()].replace("\n", " ")))
    return bad


def check_broken_links(pages):
    bad = set()
    for path, html in pages:
        for href in re.findall(r'href="(/[^"#?]*)"', strip_scripts(html)):
            if href.startswith("//"):
                continue
            target = href.lstrip("/")
            candidates = [target, os.path.join(target, "index.html")]
            if not any(os.path.exists(os.path.join(DIST, c)) for c in candidates):
                bad.add(href)
    return sorted(bad)


def check_alt_text(pages):
    bad = []
    for path, html in pages:
        main = re.search(r"<main.*?</main>", html, re.S)
        if not main:
            continue
        for img in re.findall(r"<img[^>]*>", main.group(0)):
            # An empty alt is legitimate for decorative images, but a missing
            # attribute is always a mistake.
            if "alt=" not in img:
                bad.append((path, img[:70]))
    return bad


def main():
    if not os.path.isdir(DIST):
        print(f"no build at {DIST}", file=sys.stderr)
        return 1

    pages = [
        (os.path.relpath(p, DIST), read(p))
        for p in glob.glob(f"{DIST}/**/*.html", recursive=True)
    ]

    failures = 0

    glued = check_glued_links(pages)
    if glued:
        failures += 1
        print(f"FAIL  {len(glued)} link(s) glued to the preceding word:")
        for path, snippet in glued[:6]:
            print(f"        {path}: …{snippet}")
        print("      Put {' '} before the <a>, or keep it on the same line.")

    broken = check_broken_links(pages)
    if broken:
        failures += 1
        print(f"FAIL  {len(broken)} broken internal link(s):")
        for href in broken[:10]:
            print(f"        {href}")

    noalt = check_alt_text(pages)
    if noalt:
        failures += 1
        print(f"FAIL  {len(noalt)} image(s) with no alt attribute:")
        for path, img in noalt[:6]:
            print(f"        {path}: {img}")

    if failures:
        return 1

    print(f"checks passed  ({len(pages)} pages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
