import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

/**
 * Prose lives in ../content/ at the repository root rather than inside the
 * Astro project, so it stays legible to a browser CMS and to anyone reading
 * the repo without knowing Astro.
 */
const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: '../content/pages' }),
  schema: z.object({
    title: z.string(),
    slug: z.string().optional(),
    legacyUrl: z.string().optional(),
    legacyShortcodes: z.array(z.string()).optional(),
  }),
});

export const collections = { pages };
