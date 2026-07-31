# Senan Shaibani Cultural Center

The website and public catalog for the Senan Shaibani Cultural Center, a
Middle Eastern studies research collection in Lincoln, Texas.

It is a **static site**: every page is generated ahead of time into plain HTML
files, which are then served as-is. There is no database, no server-side code,
and no login for visitors. That makes it fast, close to free to host, and
difficult to break.

- **Framework:** [Astro](https://astro.build) — a site generator that renders
  components to HTML at build time
- **Content:** Markdown files in `content/`, editable by hand or through a web
  editor at `/admin/`
- **Catalog:** exported from Zotero, transformed by a Python script at build
  time
- **Hosting:** any static host. Cloudflare Pages is what the deployment notes
  below assume.

---

## Quick start

You need **Node 22 or newer** and **Python 3.9 or newer**. Check with
`node --version` and `python3 --version`. (`.nvmrc` pins the Node version if
you use [nvm](https://github.com/nvm-sh/nvm): run `nvm use`.)

```
cd site
npm ci
npm run dev
```

Open <http://localhost:4321>. Edits to files appear in the browser
immediately, without restarting.

To produce the deployable files:

```
npm run build
```

The finished site lands in `site/dist/`. To preview exactly what will be
deployed, run `npm run preview` afterwards.

### What `npm run build` actually does

Three steps, in order:

1. `npm run catalog` — runs `tools/build_catalog.py`, which reads the Zotero
   export and writes `data/catalog.json`
2. `astro build` — renders every page to `site/dist/`
3. `npm run check` — runs `tools/check_build.py`, which inspects the output
   and **fails the build** if it finds broken links, images without alt text,
   or a link glued to the word before it

If the build fails, step 3 is the most likely culprit and it prints exactly
what is wrong.

---

## Where everything lives

| Path | What it is |
|---|---|
| `site/` | The website. Astro project — components, pages, styles, fonts |
| `content/pages/` | The words on the page, as Markdown. Safe to edit |
| `data/` | The tracked Zotero CSV; `catalog.json` is generated from it |
| `tools/` | Python scripts: catalog build, image build, output checks |

Inside `site/src/`:

| Path | What it is |
|---|---|
| `config.ts` | Site name, navigation, the three libraries, the guide list. Start here |
| `pages/` | One file per URL. `catalog/[id].astro` generates a page per record |
| `layouts/Base.astro` | The shell every page sits in: masthead, nav, footer |
| `components/Figure.astro` | Images with captions |
| `lib/catalog.ts` | Reads `catalog.json` and exposes it to pages |
| `styles/global.css` | Colors, type, spacing. All design tokens are at the top |

### The private archive is separate from this repository

Original photographs, the WordPress export, correspondence, handover files,
and private project notes live in a separate private folder outside this
repository. They are deliberately excluded from version control because they
contain personal information and large archival files.

Cloning this repository provides everything needed to run and deploy the
website. It does not provide the original archival files. Keep at least one
independent backup of that private folder. `tools/build_images.py` only needs
it when the public image derivatives themselves are being changed.

---

## Common tasks

### Change the words on a page

Most prose lives in `content/pages/*.md`. Edit the Markdown and save.

Pages that are mostly structure rather than prose — the homepage, About,
Visit — are Astro components in `site/src/pages/`. The text sits directly in
the markup; edit it there.

### Change the site name, navigation, or library descriptions

All in `site/src/config.ts`. The institution's name is a single value, so
renaming it later is one edit plus a redirect, not a search across the site.

### Publish new cataloging

The catalog is generated from Zotero, which stays the system of record.

1. Export the Zotero group library to CSV
2. Replace `data/zotero-export-rifat-al-said.csv`
3. Rebuild (or commit — the host rebuilds automatically)

`tools/build_catalog.py` re-applies every correction on each build, so the
export is never hand-edited and nobody's work in Zotero is overwritten. **Do
not edit `data/catalog.json`** — it is generated and will be overwritten.

To add a second library, drop its export into `data/` and extend the input
list in the script.

### Add a subject guide

1. Add a Markdown file to `content/pages/`
2. Add an entry to `guides` in `site/src/config.ts` with a matching `slug`

It then appears on the Guides page, in the header menu, and in the footer.
Navigation is never written by hand.

### Change the images

`tools/build_images.py` regenerates every site image from the separately held
originals and records each crop and exposure decision in code. It requires
[Pillow](https://pillow.readthedocs.io/) and the path to the private source
folder:

```bash
pip3 install pillow
SSCC_SOURCE_DIR="../sscc_private/source" python3 tools/build_images.py
```

The folder name is only an example; set `SSCC_SOURCE_DIR` to wherever the
private `source` folder is stored.

The results are committed to `site/public/img/`, so this only needs running
when the images themselves change.

---

## Deploying

Nothing has been deployed yet. These are the steps.

### 1. GitHub

Create a repository and push. Commits are authored as the center, not an
individual, via a repository-local git config.

### 2. Cloudflare Pages

Create a Pages project connected to the repository.

| Setting | Value |
|---|---|
| Build command | `npm run build` |
| Build output directory | `site/dist` |
| Root directory | `site` |

This gives a `*.pages.dev` URL. **Review the site there before touching DNS.**

### 3. The web editor

`site/public/admin/config.yml` needs two edits before anyone can sign in:

1. `repo: OWNER/REPO` — the account and repository from step 1
2. Register a GitHub OAuth app, and either point `base_url` at your own auth
   worker or keep the hosted relay

Editors then sign in at `/admin/`. Every save is a git commit, so changes are
attributable and revertible, and the content stays plain Markdown if the
editor is ever removed.

### 4. DNS — the part that needs care

**Read this before cancelling anything at WordPress.com.**

Four separate things are attached to the domain, and they move independently:

| Thing | Where it is now |
|---|---|
| Registration | WordPress.com (both `.com` and `.org`) |
| DNS | WordPress.com nameservers (`ns1–3.wordpress.com`) |
| Web hosting | WordPress.com |
| **Email** | **Titan** (`mx1.titan.email`), billed through WordPress.com |

`contact@senanshaibaniculturalcenter.org` is published on the site and in the
catalog's citation guidance. **Cancelling the WordPress.com plan may terminate
that mailbox.** Confirm with their support what happens to it before
cancelling anything.

Recommended order:

1. Verify the site on its `pages.dev` URL
2. Move DNS to Cloudflare, recreating these records exactly:
   - `MX  10  mx1.titan.email`
   - `MX  20  mx2.titan.email`
   - `TXT  "v=spf1 include:spf.titan.email include:_spf.wpcloud.com ~all"`
     (the `_spf.wpcloud.com` part can go once WordPress.com does)
3. Point the apex and `www` at the Pages project
4. Confirm mail still sends **and** receives
5. Only then consider cancelling hosting — keeping the registration and
   mailbox until they have somewhere else to live

`site/public/_redirects` preserves every URL the old site published, so
existing citations and search results keep working. Add to it rather than
removing from it.

### Analytics

`site.analyticsToken` in `config.ts` is empty, so no tracking script loads at
all. Setting it to a Cloudflare Web Analytics token enables cookieless
analytics that need no consent banner. Traffic figures are then read from the
Cloudflare dashboard.

---

## Things that will bite you

Each of these cost real time to diagnose. They are all normal behavior, not
bugs in the project.

**Astro deletes the space before an inline link.** Writing this:

```jsx
published under a
<a href="...">CC BY 4.0</a> license
```

produces `under aCC BY 4.0`. Keep the link on the same line, or write
`{' '}` before it. `npm run check` fails the build if this slips through.

**Scoped styles do not reach elements created by JavaScript.** Astro scopes
CSS with a generated attribute that only server-rendered markup carries. The
catalog rows are drawn in the browser, so their styles live in a
`<style is:global>` block with prefixed class names. If a JS-rendered element
appears unstyled, this is why.

**`getStaticPaths()` cannot see variables defined above it.** Astro lifts that
function into its own scope. Anything it needs must be declared inside it.

**A sticky element needs somewhere to travel.** In a CSS grid with
`align-items: start`, a column shrinks to its content, so a sticky child has
almost no range and appears not to stick. The guide rail sets
`align-self: stretch` for this reason.

**The dev server sometimes serves stale content** after changes to
`config.ts` or `data/catalog.json`. Restart it.

**Arabic is decided by dominance, not presence.** A value is typeset
right-to-left only when Arabic outweighs Latin in it. Names like
`Ghazālī/غزالي, ʿAbd al-Munʿim` are mixed, and marking the whole string as
Arabic reverses the Latin parts.

---

## About the catalog

Roughly 60% of the collection is in Arabic script, which drives two decisions.

**Typography.** Arabic is set in Noto Naskh Arabic, right-to-left, with its own
size and leading rather than being forced into the Latin face.

**Search.** Every record is indexed twice: once folded per script (hamza
seats, alef variants, ta marbuta and diacritics collapsed) and once as a
consonant skeleton that bridges the two. A reader typing `sahafah` and a
reader typing `صحافة` reach the same records. The romanization behind that
bridge is approximate, exists only in the search index, and is never
displayed or written back to Zotero.

Coverage is **890 records**, all from the Rifʿat al-Saʿīd Library, against an
estimated 10,000+ item holding. Subject vocabulary is left exactly as
cataloged. Any future vocabulary changes should be agreed with the cataloging
team before they are added to the build script.

---

## Known limits

- **Search index size.** `/catalog/index.json` is 561 KB (137 KB gzipped) and
  grows in step with the catalog. Past roughly 5,000 records it should move to
  a prebuilt index or [Pagefind](https://pagefind.app) rather than the current
  linear scan.
- **Subject terms are not offered as filters**, because 73% of them are used
  exactly once. This should be revisited with the cataloging team as coverage
  improves.

## License

Not yet chosen. Keep the repository private until this is decided: the
descriptive catalog records are published under CC BY 4.0 on the site itself,
but the code has no license, which by default means nobody else may reuse it.
