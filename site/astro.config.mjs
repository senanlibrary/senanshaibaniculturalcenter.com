// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://senanshaibaniculturalcenter.org',
  integrations: [sitemap()],
  build: {
    // Directory-style URLs keep catalog record links stable and citable.
    format: 'directory',
  },
  vite: {
    server: {
      // Prose and catalogue data live at the repository root, one level above
      // the Astro project.
      fs: { allow: ['..'] },
    },
  },
});
