// tools/seo-agent-pro/lib/seo.mjs
// Small, dependency-free helpers shared by the article generator.

export const SITE_URL = 'https://bankacem.github.io/GlobalScore';

export function slugify(homeEn, awayEn, id) {
  const clean = (s) =>
    s
      .toLowerCase()
      .normalize('NFKD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
  return `${clean(homeEn)}-vs-${clean(awayEn)}-${id}`;
}

// Deterministic "random" pick so re-running the generator on unchanged
// data produces identical output (important for clean git diffs / CI).
export function pick(seed, arr) {
  let h = 0;
  const s = String(seed);
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) >>> 0;
  }
  return arr[h % arr.length];
}

export function truncateMeta(text, max = 158) {
  if (text.length <= max) return text;
  const cut = text.slice(0, max);
  return cut.slice(0, cut.lastIndexOf(' ')) + '…';
}

export function escapeHtml(str = '') {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function isoDateFromMinuteless(baseDate = new Date()) {
  return baseDate.toISOString();
}

// Builds schema.org SportsEvent + BreadcrumbList + NewsArticle JSON-LD.
export function buildJsonLd({ lang, slug, title, description, match, articleType, datePublished }) {
  const url = `${SITE_URL}/${lang}/articles/${slug}.html`;
  const eventStatusMap = {
    Scheduled: 'https://schema.org/EventScheduled',
    Live: 'https://schema.org/EventScheduled',
    FT: 'https://schema.org/EventCompleted',
  };

  const sportsEvent = {
    '@context': 'https://schema.org',
    '@type': 'SportsEvent',
    name: `${match.home} vs ${match.away}`,
    sport: 'Football',
    startDate: undefined,
    eventStatus: eventStatusMap[match.status] || 'https://schema.org/EventScheduled',
    homeTeam: { '@type': 'SportsTeam', name: match.home },
    awayTeam: { '@type': 'SportsTeam', name: match.away },
    location: { '@type': 'Place', name: match.league },
    ...(match.status === 'FT'
      ? {
          homeTeamScore: Number(match.score.split('-')[0].trim()),
          awayTeamScore: Number(match.score.split('-')[1].trim()),
        }
      : {}),
  };

  const breadcrumb = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'GlobalScore', item: `${SITE_URL}/${lang}/` },
      { '@type': 'ListItem', position: 2, name: lang === 'ar' ? 'المقالات' : 'Articles', item: `${SITE_URL}/${lang}/articles/` },
      { '@type': 'ListItem', position: 3, name: title, item: url },
    ],
  };

  const article = {
    '@context': 'https://schema.org',
    '@type': articleType === 'preview' ? 'Article' : 'NewsArticle',
    headline: title,
    description,
    inLanguage: lang,
    datePublished,
    dateModified: datePublished,
    mainEntityOfPage: url,
    publisher: {
      '@type': 'Organization',
      name: 'GlobalScore',
      logo: { '@type': 'ImageObject', url: `${SITE_URL}/assets/img/logo.svg` },
    },
    about: { '@type': 'SportsEvent', name: `${match.home} vs ${match.away}` },
  };

  return [sportsEvent, breadcrumb, article]
    .map((obj) => `<script type="application/ld+json">${JSON.stringify(obj)}</script>`)
    .join('\n');
}
