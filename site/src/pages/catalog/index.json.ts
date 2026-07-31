import type { APIRoute } from 'astro';
import { items } from '../../lib/catalog';

/**
 * Compact search index for the browse page.
 *
 * Field names are single letters because this file is downloaded by every
 * visitor to the catalog, and the collection is expected to grow past
 * 10,000 records. Full descriptive records stay on their own static pages.
 */
export const GET: APIRoute = async () =>
  new Response(
    JSON.stringify(
      items.map((i) => ({
        i: i.id,
        t: i.title,
        a: i.titleArabic,
        u: i.authors[0] ?? i.editors[0] ?? '',
        y: i.year,
        l: i.languages,
        r: i.location.range,
        c: i.location.display,
        s: i.search,
        k: i.skeleton,
      }))
    ),
    { headers: { 'Content-Type': 'application/json' } }
  );
