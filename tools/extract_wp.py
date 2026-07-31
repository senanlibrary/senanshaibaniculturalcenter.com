#!/usr/bin/env python3
"""Extract pages from the WordPress export into Markdown with YAML front matter.

Run once to rescue content off WordPress.com; kept in the repo so the
conversion is reproducible and auditable rather than a one-off hand edit.
"""
import html
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
}
UPLOAD_RE = re.compile(r"https?://[^\"'\s)]*?/wp-content/uploads/([^\"'\s)]+)")


def local_asset(url):
    """Rewrite a WordPress upload URL to the site's public uploads path."""
    m = UPLOAD_RE.search(url)
    return "/uploads/" + urllib.parse.unquote(m.group(1)) if m else url


def to_markdown(raw):
    """Convert WordPress block HTML to Markdown.

    The export is Gutenberg output, so the markup is regular: block comments
    wrap ordinary h1-h6/p/ul/img/figure/table elements.
    """
    s = re.sub(r"<!--\s*/?wp:.*?-->", "", raw, flags=re.S)

    # Images: keep alt text, point at the mirrored asset.
    def img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        if not src:
            return ""
        return f"\n![{alt.group(1) if alt else ''}]({local_asset(src.group(1))})\n"

    s = re.sub(r"<img[^>]*>", img, s)
    s = re.sub(r"</?figure[^>]*>", "\n", s)
    s = re.sub(r"<figcaption[^>]*>(.*?)</figcaption>", r"\n*\1*\n", s, flags=re.S)

    # Links before other inline handling so hrefs survive.
    s = re.sub(
        r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        lambda m: f"[{m.group(2)}]({m.group(1)})",
        s,
        flags=re.S,
    )

    # The original authors used heading blocks for body copy. Length alone
    # misfires here: several legitimate headings are long transliterated or
    # Arabic book titles. A mid-string sentence break is the reliable tell,
    # since titles carry colons and slashes but rarely ". " followed by more.
    def heading(m, lvl):
        text = m.group(1).strip()
        plain = re.sub(r"<[^>]+>", "", text)
        is_prose = len(plain) > 120 and re.search(r"[.!?؟]\s+\S", plain)
        if is_prose:
            return f"\n\n{text}\n\n"
        return f"\n\n{'#' * lvl} {text}\n\n"

    for lvl in range(1, 7):
        s = re.sub(
            rf"<h{lvl}[^>]*>(.*?)</h{lvl}>",
            lambda m, l=lvl: heading(m, l),
            s,
            flags=re.S,
        )

    s = re.sub(r"<li[^>]*>(.*?)</li>", r"\n- \1", s, flags=re.S)
    s = re.sub(r"</?(ul|ol)[^>]*>", "\n", s)
    def emphasis(marker):
        """Move padding from inside the emphasis markers to outside.

        Markdown ignores "**bold **" but HTML does not, and the source is full
        of "<strong>About: </strong>". Doing this while the tags still delimit
        the run avoids guessing at marker boundaries later.
        """

        def repl(m):
            inner = m.group(2)
            stripped = inner.strip()
            if not stripped:
                return " "
            lead = " " if inner[:1].isspace() else ""
            trail = " " if inner[-1:].isspace() else ""
            return f"{lead}{marker}{stripped}{marker}{trail}"

        return repl

    s = re.sub(r"<(strong|b)[^>]*>(.*?)</\1>", emphasis("**"), s, flags=re.S)
    s = re.sub(r"<(em|i)[^>]*>(.*?)</\1>", emphasis("*"), s, flags=re.S)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n\n", s)
    s = re.sub(r"<[^>]+>", "", s)

    s = html.unescape(s)
    s = s.replace(" ", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def yaml_quote(v):
    return '"' + str(v).replace('"', '\\"') + '"'


def main(xml_path, outdir):
    channel = ET.parse(xml_path).getroot().find("channel")
    os.makedirs(outdir, exist_ok=True)
    written = []

    for item in channel.findall("item"):
        if item.findtext("wp:post_type", namespaces=NS) != "page":
            continue
        if item.findtext("wp:status", namespaces=NS) != "publish":
            continue

        title = item.findtext("title") or "untitled"
        slug = item.findtext("wp:post_name", namespaces=NS) or "untitled"
        raw = item.find("content:encoded", namespaces=NS).text or ""
        shortcodes = re.findall(r"\[[a-z_]+[^\]]*\]", raw)

        front = [
            "---",
            f"title: {yaml_quote(title)}",
            f"slug: {yaml_quote(slug)}",
            f"legacyUrl: {yaml_quote(item.findtext('link'))}",
        ]
        if shortcodes:
            # Flag anything that depended on a WordPress plugin so it is
            # obvious what still needs a native replacement.
            front.append("legacyShortcodes:")
            front += [f"  - {yaml_quote(sc)}" for sc in shortcodes]
        front += ["---", ""]

        path = os.path.join(outdir, f"{slug}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(front) + to_markdown(raw))
        written.append((slug, len(raw)))

    for slug, n in written:
        print(f"  wrote {slug}.md  (from {n} chars of block HTML)")
    print(f"{len(written)} pages extracted to {outdir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
