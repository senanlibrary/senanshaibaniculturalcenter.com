import type { APIContext } from 'astro';
import { site } from '../../config';
import { url } from '../../lib/paths';
import { getUpdates } from '../../lib/updates';

const escape = (s: string) =>
  s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

export async function GET(context: APIContext) {
  const origin = context.site ?? new URL(site.url);
  const posts = await getUpdates();
  const abs = (path: string) => new URL(url(path), origin).href;

  const items = posts
    .map(
      (post) => `    <item>
      <title>${escape(post.data.title)}</title>
      <link>${abs(`/updates/${post.id}/`)}</link>
      <guid>${abs(`/updates/${post.id}/`)}</guid>
      <pubDate>${post.data.date.toUTCString()}</pubDate>${
        post.data.summary
          ? `\n      <description>${escape(post.data.summary)}</description>`
          : ''
      }
    </item>`,
    )
    .join('\n');

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escape(site.name)} — Updates</title>
    <link>${abs('/updates/')}</link>
    <description>${escape(`News from the ${site.name}.`)}</description>
${items}
  </channel>
</rss>
`;

  return new Response(xml, {
    headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' },
  });
}
