/**
 * Build an internal URL that survives being served from a subdirectory.
 *
 * The site is designed to live at the root of a domain, and normally does.
 * GitHub project Pages is the exception: it serves the site under
 * `/<repository-name>/`, so a link written as `/catalog/` resolves against
 * the organization root and 404s.
 *
 * Every internal link, image, font, and fetch should go through this. At the
 * root (the default) it returns the path unchanged, so nothing is lost by
 * using it everywhere.
 *
 *   url('/catalog/')   ->  '/catalog/'                 at the root
 *                      ->  '/repo-name/catalog/'       under a project path
 */
export function url(path: string): string {
  // import.meta.env.BASE_URL is set by Astro from the `base` config option.
  // It always has a trailing slash; paths here always have a leading one.
  const base = import.meta.env.BASE_URL;
  if (!path.startsWith('/')) return path;
  return `${base.replace(/\/$/, '')}${path}`;
}
