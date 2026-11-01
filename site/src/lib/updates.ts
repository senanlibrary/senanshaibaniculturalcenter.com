import { getCollection } from 'astro:content';

/** Published updates, newest first. Drafts appear only in the dev server. */
export async function getUpdates() {
  const all = await getCollection('updates');
  return all
    .filter((post) => import.meta.env.DEV || !post.data.draft)
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

/** "1 November 2026", fixed to UTC so the date never shifts by timezone. */
export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'UTC',
  });
}
