#!/usr/bin/env node
// tools/seo-agent-pro/generate-articles.mjs
//
// seo_agent_pro — generates professional, unique, SEO-optimised match
// articles (previews / live updates / full-time reports) for GlobalScore
// from assets/data/live.json, in both English and Arabic.
//
// Usage:
//   node tools/seo-agent-pro/generate-articles.mjs
//
// Output:
//   en/articles/<slug>.html          en/articles/index.html
//   ar/articles/<slug>.html          ar/articles/index.html
//   sitemap.xml                      (article URLs appended)

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { slugify, SITE_URL } from './lib/seo.mjs';
import { buildEnglishArticle } from './lib/content-en.mjs';
import { buildArabicArticle } from './lib/content-ar.mjs';
import { renderArticlePage, renderIndexPage } from './lib/layout.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..', '..'); // repo root

const DATA_PATH = path.join(ROOT, 'assets', 'data', 'live.json');
const OUT_DIRS = {
  en: path.join(ROOT, 'en', 'articles'),
  ar: path.join(ROOT, 'ar', 'articles'),
};
const CSS_SRC = path.join(__dirname, 'output-assets', 'articles.css');
const CSS_DEST = path.join(ROOT, 'assets', 'css', 'articles.css');
const SITEMAP_PATH = path.join(ROOT, 'sitemap.xml');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function main() {
  if (!fs.existsSync(DATA_PATH)) {
    console.error(`[seo_agent_pro] Could not find data file at ${DATA_PATH}`);
    process.exit(1);
  }

  const data = readJson(DATA_PATH);
  const matches = data.matches || [];
  if (!matches.length) {
    console.warn('[seo_agent_pro] No matches found in live.json — nothing to generate.');
    return;
  }

  ensureDir(OUT_DIRS.en);
  ensureDir(OUT_DIRS.ar);
  ensureDir(path.dirname(CSS_DEST));
  fs.copyFileSync(CSS_SRC, CSS_DEST);

  const datePublished = new Date().toISOString();
  const indexItems = { en: [], ar: [] };
  const sitemapUrls = [];

  for (const match of matches) {
    const slug = slugify(match.home, match.away, match.id);

    const en = buildEnglishArticle(match);
    const ar = buildArabicArticle(match);

    const enHtml = renderArticlePage({
      lang: 'en',
      slug,
      title: en.title,
      description: en.description,
      bodyHtml: en.body,
      match,
      articleType: en.type,
      datePublished,
    });
    const arHtml = renderArticlePage({
      lang: 'ar',
      slug,
      title: ar.title,
      description: ar.description,
      bodyHtml: ar.body,
      match,
      articleType: ar.type,
      datePublished,
    });

    fs.writeFileSync(path.join(OUT_DIRS.en, `${slug}.html`), enHtml, 'utf8');
    fs.writeFileSync(path.join(OUT_DIRS.ar, `${slug}.html`), arHtml, 'utf8');

    indexItems.en.push({ slug, title: en.title, league: match.league });
    indexItems.ar.push({ slug, title: ar.title, league: match.leagueAr || match.league });

    sitemapUrls.push(`${SITE_URL}/en/articles/${slug}.html`);
    sitemapUrls.push(`${SITE_URL}/ar/articles/${slug}.html`);

    console.log(`[seo_agent_pro] generated: ${slug} (${match.status})`);
  }

  fs.writeFileSync(
    path.join(OUT_DIRS.en, 'index.html'),
    renderIndexPage({ lang: 'en', items: indexItems.en }),
    'utf8'
  );
  fs.writeFileSync(
    path.join(OUT_DIRS.ar, 'index.html'),
    renderIndexPage({ lang: 'ar', items: indexItems.ar }),
    'utf8'
  );

  updateSitemap(sitemapUrls, datePublished);

  console.log(`\n[seo_agent_pro] Done. ${matches.length} matches -> ${matches.length * 2} articles (EN + AR).`);
}

function updateSitemap(urls, lastmod) {
  if (!fs.existsSync(SITEMAP_PATH)) {
    console.warn('[seo_agent_pro] sitemap.xml not found, skipping sitemap update.');
    return;
  }
  let xml = fs.readFileSync(SITEMAP_PATH, 'utf8');
  const day = lastmod.slice(0, 10);

  const newEntries = urls
    .filter((u) => !xml.includes(u))
    .map((u) => `  <url>\n    <loc>${u}</loc>\n    <lastmod>${day}</lastmod>\n  </url>`)
    .join('\n');

  if (!newEntries) return;

  if (xml.includes('</urlset>')) {
    xml = xml.replace('</urlset>', `${newEntries}\n</urlset>`);
  } else {
    xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${newEntries}\n</urlset>\n`;
  }
  fs.writeFileSync(SITEMAP_PATH, xml, 'utf8');
  console.log(`[seo_agent_pro] sitemap.xml updated with ${urls.filter((u) => xml.includes(u)).length / 1} entries.`);
}

main();
