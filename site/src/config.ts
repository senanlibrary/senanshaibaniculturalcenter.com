/**
 * Institutional identity lives here, in one place.
 *
 * The center is expected to be renamed at some point (see the project's
 * naming discussion). Keeping the name, short name, and domain as single
 * values means that change is an edit here plus DNS redirects, not a sweep
 * through every template.
 */
export const site = {
  name: 'Senan Shaibani Cultural Center',
  shortName: 'Senan Shaibani',
  /** Used where "the Library" reads more naturally than the full name. */
  libraryWord: 'the Library',
  tagline: 'A research collection in Middle Eastern studies',
  location: 'Lincoln, Texas',
  email: 'contact@senanshaibaniculturalcenter.org',
  url: 'https://senanshaibaniculturalcenter.org',
  /**
   * Cloudflare Web Analytics token. Cookieless, collects no personal data,
   * and needs no consent banner. Leave empty and no script is loaded at all.
   * Obtained from the Cloudflare dashboard after deploying; see the
   * Analytics section of the repository README.
   */
  analyticsToken: '',
} as const;

/**
 * Subject guides. The slug matches the Markdown file in content/pages, so
 * adding a guide means adding a file and an entry here -- the navigation is
 * never hardcoded into the prose itself, which is what caused the duplicated
 * links inherited from WordPress.
 */
export const guides = [
  {
    slug: 'serials',
    title: 'Serials and periodicals',
    blurb:
      'Journals and serial publications from the United States, Egypt, Iraq, and Palestine, several of them held nowhere else in the country.',
  },
  {
    slug: 'journalism-in-the-arab-world',
    title: 'Journalism in the Arab world',
    blurb:
      'Arabic-language works on the history of the press, from the nineteenth-century Egyptian and Lebanese papers to the Nasser era.',
  },
  {
    slug: 'women-in-the-arab-world',
    title: 'Women in the Arab world',
    blurb:
      'Writing by and about women across the region — memoir, activism, literary criticism, and social research.',
  },
] as const;

export const nav = [
  { href: '/catalog/', label: 'Catalog' },
  { href: '/collections/', label: 'Collections' },
  {
    href: '/guides/',
    label: 'Guides',
    // A section of its own rather than a sub-page of Collections: the guides
    // are the most useful thing here, and burying them made the site map
    // read oddly.
    children: guides.map((g) => ({
      href: `/guides/${g.slug}/`,
      label: g.title,
    })),
  },
  { href: '/about/', label: 'About' },
  { href: '/visit/', label: 'Visit' },
] as const;


/** The three physical collections held at the center. */
export const libraries = [
  {
    slug: 'rifat-al-said',
    name: 'Rifʿat al-Saʿīd Library',
    summary:
      'Smaller in size, this library houses many of the journal collections, including a range of titles from Egypt as well as materials from the journalism collection.',
    cataloged: true,
  },
  {
    slug: 'barbara-harlow',
    name: 'Barbara Harlow Library',
    summary:
      'The main library, in the reading room. Dedicated to the late Barbara Harlow, a pivotal scholar whose work centered on women of the region, postcolonial thinking, and human rights activism. Many of the books come from her personal collection.',
    cataloged: false,
  },
  {
    slug: 'ismail-archives',
    name: 'Dr. Tariq and Jacqueline Ismail Archives',
    summary:
      'Dedicated to Tariq and Jacqueline Ismail, distinguished scholars who worked out of Calgary and founded the International Journal of Contemporary Iraqi Studies. Their personal library, with an extensive archive of Middle Eastern newspapers, posters, and memorabilia.',
    cataloged: false,
  },
] as const;
