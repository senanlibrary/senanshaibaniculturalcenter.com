#!/usr/bin/env python3
"""Rebuild the site's images from a separately held private source folder.

The site uses very few images, each deliberately chosen and cropped. This
script records those decisions so they can be repeated, adjusted, or undone
by someone who was not there when they were made.

    pip3 install pillow
    SSCC_SOURCE_DIR="../sscc_private/source" python3 tools/build_images.py

Nothing here runs during a normal build: the results are committed to
site/public/img/. Run it only when changing which images the site uses, or
how they are cropped.

Two rules the layout depends on:

  * Every scene photograph is delivered at the same 16:9 frame, so pages feel
    consistent as you move between them.
  * Objects from the collection -- a portrait, a book jacket -- keep their own
    proportions. Cropping an artifact to fit a template misrepresents it.
"""
import os
import sys

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError:
    sys.exit("Pillow is required:  pip3 install pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(os.path.dirname(ROOT), "sscc_private", "source")
SRC = os.path.abspath(os.environ.get("SSCC_SOURCE_DIR", DEFAULT_SRC))
OUT = os.path.join(ROOT, "site", "public", "img")

WIDE = 16 / 9


def save(im, name, width, quality=82):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im = im.resize((width, round(width * im.size[1] / im.size[0])), Image.LANCZOS)
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    print(f"  {name:24} {os.path.getsize(path) // 1024:4} KB  {im.size[0]}x{im.size[1]}")


def wide(path, left=0.0, width=1.0, top=0.5, brightness=1.0, autocontrast=0):
    """Crop to the shared 16:9 frame.

    left/width select a horizontal slice of the original (fractions of its
    width), top positions the crop vertically. The interiors were shot against
    bright windows, so the room itself sits several stops down and needs
    lifting before it goes on the page.
    """
    im = Image.open(path).convert("RGB")
    if autocontrast:
        im = ImageOps.autocontrast(im, cutoff=autocontrast)
    if brightness != 1.0:
        im = ImageEnhance.Brightness(im).enhance(brightness)
    w, h = im.size
    cw = int(w * width)
    cl = int(w * left)
    ch = int(cw / WIDE)
    ct = int((h - ch) * top)
    return im.crop((cl, ct, cl + cw, ct + ch))


def main():
    os.makedirs(OUT, exist_ok=True)

    # Homepage. Cropped to the left two-thirds: the windows on the right blow
    # out and the glare was the first thing the eye landed on.
    save(
        wide(
            f"{SRC}/media/as_images/IMG_4935.jpeg",
            left=0.0, width=0.66, top=0.45, brightness=1.35, autocontrast=1,
        ),
        "reading-room.jpg", 2000,
    )

    # Visit.
    save(wide(f"{SRC}/media/as_images/IMG_4959 2.jpeg"), "stone-marker.jpg", 1400)

    # Women in the Arab World. The original is a stereograph -- two nearly
    # identical frames side by side -- which reads as a printing error on a
    # web page. Take the left frame only, then crop to the shared 16:9.
    stereo = Image.open(
        f"{SRC}/wordpress-export/uploads/2026/04/palestine-00068-1.jpeg"
    ).crop((150, 120, 2970, 4270))
    fw, fh = stereo.size
    th = int(fw / WIDE)
    save(stereo.crop((0, int(fh * 0.20), fw, int(fh * 0.20) + th)), "bride-nazareth.jpg", 1400)

    # About. Portrait, so no 16:9 crop; the black pillarbox bars are trimmed.
    senan = Image.open(
        f"{SRC}/wordpress-export/uploads/2026/04/e4273d00-7e92-40d0-a1bd-f3f377594fd8.jpeg"
    ).crop((43, 0, 743, 1001))
    save(senan, "senan.jpg", 620, quality=85)

    # Journalism guide. Six jackets, scanned from one low-resolution sheet and
    # cropped by hand into source/media/as_cropped. Kept at native size and
    # shown small on the page so they stay sharp.
    for i in range(1, 7):
        src = f"{SRC}/media/as_cropped/{i}.jp2"
        if not os.path.exists(src):
            print(f"  covers/{i}.jpg  MISSING {src}")
            continue
        im = Image.open(src).convert("RGB")
        save(im, f"covers/{i}.jpg", im.size[0], quality=90)


if __name__ == "__main__":
    if not os.path.isdir(SRC):
        sys.exit(
            f"Private source folder not found: {SRC}\n"
            "Set SSCC_SOURCE_DIR to the folder containing media/ and\n"
            "wordpress-export/, then run this command again."
        )
    main()
