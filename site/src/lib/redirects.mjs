import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

/**
 * Read the redirect table.
 *
 * Every address the old WordPress site published has to keep working: they
 * appear in the cataloging team's documentation, in anything anyone has
 * bookmarked, and in search results. A redirect is what completes a
 * migration — the old page is gone, but its address still leads somewhere.
 *
 * GitHub Pages cannot send a real 301, so each of these is built as a small
 * HTML page that forwards immediately. The table stays in one plain text
 * file: `from  to` per line, `#` for comments.
 */
export function readRedirects() {
  // Resolved from the Astro project root rather than import.meta.url, which
  // does not survive bundling into the prerender entrypoint.
  const path = resolve(process.cwd(), 'src/redirects.txt');
  return readFileSync(path, 'utf-8')
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'))
    .map((line) => {
      const [from, to] = line.split(/\s+/);
      return { from, to };
    })
    .filter((r) => r.from && r.to);
}
