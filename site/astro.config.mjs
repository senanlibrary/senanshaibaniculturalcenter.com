// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readRedirects } from './src/lib/redirects.mjs';

// Forwarding pages must stay out of the sitemap: they are signposts to the
// real pages, not content in their own right.
const redirectPaths = new Set(readRedirects().map((r) => r.from));

/**
 * Where the site lives.
 *
 * The permanent home is the custom domain at the root of its host, and that
 * is the default here — local development and the eventual production site
 * both need no configuration at all.
 *
 * GitHub project Pages is the exception: it serves from a subdirectory named
 * after the repository, so every internal link has to carry that prefix. The
 * deploy workflow sets these two variables for that build alone. When DNS
 * moves and a custom domain is attached, delete them from the workflow and
 * everything returns to root without touching a line of site code.
 */
const site = process.env.SITE_URL ?? 'https://senanshaibaniculturalcenter.org';
const base = process.env.BASE_PATH ?? '/';

export default defineConfig({
  site,
  base,
  integrations: [
    sitemap({
      filter: (page) => {
        const path = new URL(page).pathname.replace(base.replace(/\/$/, ''), '');
        return !redirectPaths.has(path);
      },
    }),
  ],
  build: {
    // Directory-style URLs keep catalog record links stable and citable.
    format: 'directory',
  },
  vite: {
    server: {
      // Prose and catalog data live at the repository root, one level above
      // the Astro project.
      fs: { allow: ['..'] },
    },
  },
});
