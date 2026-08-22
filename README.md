# GlobalScore

GlobalScore is a static, mobile-first football hub for live-score presentation, upcoming fixtures, league tables, original match reports, tactical notes, and player-watch stories. It is designed for GitHub Pages and does not require a paid service to run the current demo.

## What changed

The interface now has a clear editorial hierarchy: a branded hero, a daily match board, upcoming fixtures, original stories, a league sidebar, favourites, dark mode, multilingual navigation, and accessible focus/skip-link states. Arabic and English homepages use matching canonical and `hreflang` metadata, while every article has its own canonical URL and structured Article metadata.

The content layer is intentionally local. `assets/data/live.json` contains the current demo scoreboard and standings, while `assets/data/content.json` contains fixture cards and editorial stories. This keeps GitHub Pages deployment free and predictable. The previous five-second random live-score simulator was removed so the site does not present fabricated changes as real-time data.

## Free data upgrade path

The front end can later consume a generated JSON snapshot from a free public source, but API credentials must never be placed in this static repository. A safe approach is to run a scheduled build outside the browser, write a sanitised JSON snapshot into `assets/data/`, and deploy the result to GitHub Pages. API-Football advertises a no-card free plan with a daily request limit, and TheSportsDB advertises an open free sports API; both should be checked against their current terms before production use.

Until that connection is configured, the site clearly labels its local scores and fixtures as demo data.

## Sitemap and Search Console

The repository now includes both `Sitemap.xml` and `sitemap.xml` for compatibility with the URL previously submitted to Search Console. The root sitemap lists the English and Arabic homepages plus all six article pages using absolute URLs. `robots.txt` references both spellings, and `sitemap-index.xml` points to the canonical root sitemap.

Submit this exact URL in Google Search Console:

```text
https://bankacem.github.io/GlobalScore/Sitemap.xml
```

After GitHub Pages publishes the commit, open the URL in a browser and confirm that it returns XML rather than an HTML 404 page. Google recommends absolute canonical URLs, UTF-8 XML, and a sitemap at the site root; a sitemap improves discovery but does not guarantee indexing.

## Local development

Because the site uses JavaScript modules, serve it through a local HTTP server:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173/en/` or `http://localhost:4173/ar/`.

## Project structure

```text
/en/ and /ar/                 multilingual homepages
/en/articles/ and /ar/articles/  indexable editorial pages
/assets/data/live.json         demo scores and standings
/assets/data/content.json      fixtures and editorial content
/assets/js/                    data loading, rendering, favourites and theme logic
/assets/css/                   critical and full responsive styling
Sitemap.xml                    root sitemap requested by Search Console
sitemap.xml                    lowercase compatibility copy
sitemap-index.xml              sitemap index
robots.txt                     crawler directives
```

## Editorial workflow

To publish a new article, add the Arabic and English HTML pages under their respective `articles/` directories, add a bilingual entry to `assets/data/content.json`, and add both canonical URLs to `Sitemap.xml` and `sitemap.xml`. Keep the title, description, publication date, canonical URL, and `hreflang` links consistent.
