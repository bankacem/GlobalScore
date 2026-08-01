// tools/seo-agent-pro/lib/layout.mjs
import { SITE_URL, buildJsonLd, truncateMeta } from './seo.mjs';

const NAV = {
  en: { home: 'Home', articles: 'Articles', today: 'Today', live: 'Live' },
  ar: { home: 'الرئيسية', articles: 'المقالات', today: 'اليوم', live: 'مباشر' },
};

export function renderArticlePage({ lang, slug, title, description, bodyHtml, match, articleType, datePublished }) {
  const other = lang === 'en' ? 'ar' : 'en';
  const dir = lang === 'ar' ? 'rtl' : 'ltr';
  const nav = NAV[lang];
  const url = `${SITE_URL}/${lang}/articles/${slug}.html`;
  const otherUrl = `${SITE_URL}/${other}/articles/${slug}.html`;
  const desc = truncateMeta(description);
  const jsonLd = buildJsonLd({ lang, slug, title, description: desc, match, articleType, datePublished });

  return `<!DOCTYPE html>
<html lang="${lang}" dir="${dir}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title} | GlobalScore</title>
<meta name="description" content="${desc}">
<link rel="canonical" href="${url}">
<link rel="alternate" hreflang="${lang}" href="${url}">
<link rel="alternate" hreflang="${other}" href="${otherUrl}">
<link rel="manifest" href="../../manifest.json">

<meta property="og:type" content="article">
<meta property="og:title" content="${title}">
<meta property="og:description" content="${desc}">
<meta property="og:url" content="${url}">
<meta property="og:site_name" content="GlobalScore">
<meta name="twitter:card" content="summary">

<link rel="stylesheet" href="../../assets/css/critical.css">
<link rel="stylesheet" href="../../assets/css/main.css" media="print" onload="this.media='all'">
<link rel="stylesheet" href="../../assets/css/articles.css" media="print" onload="this.media='all'">
<noscript>
  <link rel="stylesheet" href="../../assets/css/main.css">
  <link rel="stylesheet" href="../../assets/css/articles.css">
</noscript>

${jsonLd}
</head>
<body>

<header class="header">
  <div class="header-container">
    <div class="logo-container">
      <img src="../../assets/img/logo.svg" alt="GlobalScore" class="logo-img">
      <a href="../" class="logo">GlobalScore</a>
    </div>
    <nav class="nav">
      <a href="../#today" class="nav-link">${nav.today}</a>
      <a href="../#live" class="nav-link">${nav.live}</a>
      <a href="./" class="nav-link active">${nav.articles}</a>
    </nav>
  </div>
</header>

<main class="article-main">
  <p class="article-breadcrumbs">
    <a href="../">${nav.home}</a> / <a href="./">${nav.articles}</a> / <span>${title}</span>
  </p>
  <h1 class="article-title">${title}</h1>
  <p class="article-meta">GlobalScore &middot; ${new Date(datePublished).toISOString().slice(0, 10)}</p>
  <div class="article-body">
    ${bodyHtml}
  </div>
  <a class="article-back-link" href="../#today">${lang === 'ar' ? '← عودة لكل المباريات' : '← Back to all matches'}</a>
</main>

<footer class="footer">
  <p>© 2026 GlobalScore. All rights reserved.</p>
</footer>

</body>
</html>
`;
}

export function renderIndexPage({ lang, items }) {
  const dir = lang === 'ar' ? 'rtl' : 'ltr';
  const nav = NAV[lang];
  const heading = lang === 'ar' ? 'مقالات وتقارير المباريات' : 'Match Reports & Previews';
  const list = items
    .map(
      (it) => `<li><a href="./${it.slug}.html"><span>${it.title}</span><span class="article-index-meta">${it.league}</span></a></li>`
    )
    .join('\n');

  return `<!DOCTYPE html>
<html lang="${lang}" dir="${dir}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${heading} | GlobalScore</title>
<meta name="description" content="${lang === 'ar' ? 'أحدث تقارير المباريات ومعاينات اللقاءات القادمة لجميع البطولات على GlobalScore.' : 'The latest match reports and upcoming fixture previews across every league, on GlobalScore.'}">
<link rel="canonical" href="${SITE_URL}/${lang}/articles/">
<link rel="stylesheet" href="../../assets/css/critical.css">
<link rel="stylesheet" href="../../assets/css/main.css">
<link rel="stylesheet" href="../../assets/css/articles.css">
</head>
<body>
<header class="header">
  <div class="header-container">
    <div class="logo-container">
      <img src="../../assets/img/logo.svg" alt="GlobalScore" class="logo-img">
      <a href="../" class="logo">GlobalScore</a>
    </div>
    <nav class="nav">
      <a href="../#today" class="nav-link">${nav.today}</a>
      <a href="../#live" class="nav-link">${nav.live}</a>
      <a href="./" class="nav-link active">${nav.articles}</a>
    </nav>
  </div>
</header>
<main class="article-main">
  <h1 class="article-title">${heading}</h1>
  <ul class="articles-index-list">
    ${list}
  </ul>
</main>
<footer class="footer">
  <p>© 2026 GlobalScore. All rights reserved.</p>
</footer>
</body>
</html>
`;
}
